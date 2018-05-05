from collections import OrderedDict

import six
from six.moves import configparser



class LineTrackingMixin(object):
    def __init__(self, *args, **kwds):
        # Let the base class set itself up
        super(LineTrackingMixin, self).__init__(*args, **kwds)

        # It can be done with some clever wrapping of classes, but it's a pain
        if not issubclass(self._dict, OrderedDict):
            raise TypeError("The only allowed dict_type is OrderedDict (for now)")

        self._option_lines = {}

        # State:
        # lineno = None, reading_file = None    => not reading
        # lineno = int, reading_file = str    => reading lines
        # lineno = None, reading_file = str    => finalizing parsing
        self._curr_lineno = None
        self._curr_filename = None

        # self._sections, etc, have been initialized, so we can
        # wrap self._dict now. Use that for the base class just in case
        # the user passed in something custom.

        class LineNumberDict(self._dict):
            def __setitem__(inner, key, value):
                self._set_location(key)
                super(LineNumberDict, inner).__setitem__(key, value)

        self._dict = LineNumberDict

        class FpWrapper(object):
            def __init__(inner, fp):
                inner.fp = fp
                self._curr_lineno = None

            def readline(inner):
                line = inner.fp.readline()
                if not line:
                    self._curr_lineno = None
                elif self._curr_lineno is None:
                    self._curr_lineno = 1
            
            def __iter__(inner):
                for line in inner.fp:
                    if self._curr_lineno is None:
                        self._curr_lineno = 1
                    else:
                        self._curr_lineno += 1
                    yield line
                self._curr_lineno = None
        self._fp_wrapper = FpWrapper

    def _set_location(self, option, sectname=None):
        if self._curr_lineno is not None:
            if sectname is None:
                sectname = next(reversed(self._sections))
            location = self._curr_filename, self._curr_lineno
            self._option_lines[sectname, option] = location
        elif self._curr_filename is None and sectname is not None:
            self._option_lines.pop((sectname, option), None)


    def _read(self, fp, fpname):
        self._curr_filename = fpname
        fp = self._fp_wrapper(fp)
        try:
            super(LineTrackingMixin, self)._read(fp, fpname)
        finally:
            self._curr_filename = None
            self._curr_lineno = None

    def set(self, section, option, *args, **kwargs):
        self._set_location(option, section)
        return super(LineTrackingMixin, self).set(section, option, *args, **kwargs)

    def get_location(self, section, option):
        if not self.has_option(section, option):
            raise configparser.NoOptionError(option, section)
        return self._option_lines.get((section, option))

    def get_line(self, section, option):
        if not self.has_option(section, option):
            raise configparser.NoOptionError(option, section)
        return self._option_lines.get((section, option), (None,None))[1]

    def get_filename(self, section, option):
        if not self.has_option(section, option):
            raise configparser.NoOptionError(option, section)
        return self._option_lines.get((section, option), (None,None))[0]


class RawConfigParser(LineTrackingMixin, configparser.RawConfigParser):
    pass

class ConfigParser(LineTrackingMixin, configparser.ConfigParser):
    pass

class SafeConfigParser(LineTrackingMixin, configparser.SafeConfigParser):
    pass
