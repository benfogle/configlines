from collections import OrderedDict

import six
from six.moves import configparser



class LineTrackingMixin(object):
    def __init__(self):
        # We'll call constructors explicitly to ensure that this happens after
        # the main base class.

        if not issubclass(self._dict, OrderedDict):
            # It can probably be done with some clever wrapping of classes, but
            # it's a pain
            raise TypeError("The only allowed dict_type is OrderedDict "
                            "(for now)")

        self._option_lines = {}

        # State:
        # lineno = None, reading_file = None    => not reading
        # lineno = int, reading_file = str    => reading lines
        # lineno = None, reading_file = str    => finalizing parsing
        self._curr_lineno = None
        self._curr_filename = None

        # Use self._dict as the base class in case the user used something
        # custom. Hold on to a reference though, because it may change

        dict_base = self._dict
        class OptionWrapper(self._dict):
            def __init__(inner, *args, **kwargs):
                inner.sectname = None
                dict_base.__init__(inner, *args, **kwargs)

            def __setitem__(inner, key, value):
                if inner.sectname is not None:
                    self._set_location(inner.sectname, key)
                dict_base.__setitem__(inner, key, value)

        class SectionWrapper(self._dict):
            def __setitem__(inner, key, value):
                value.sectname = key
                dict_base.__setitem__(inner, key, value)

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
                else:
                    self._curr_lineno += 1
                return line
            
            def __iter__(inner):
                for line in inner.fp:
                    if self._curr_lineno is None:
                        self._curr_lineno = 1
                    else:
                        self._curr_lineno += 1
                    yield line
                self._curr_lineno = None
        self._fp_wrapper = FpWrapper

        self._dict = OptionWrapper
        self._sections = SectionWrapper()
        self._defaults = OptionWrapper(self._defaults)
        self._defaults.sectname = configparser.DEFAULTSECT

    def _set_location(self, sectname, option):
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
        self._set_location(section, option)
        return super(LineTrackingMixin, self).set(section, option, *args, **kwargs)

    def get_location(self, section, option):
        if not self.has_option(section, option):
            raise configparser.NoOptionError(option, section)
        loc = self._option_lines.get((section, option))
        if loc is None and option in self._defaults:
            return self._option_lines.get((configparser.DEFAULTSECT, option))
        return loc

    def get_line(self, section, option):
        loc = self.get_location(section, option)
        if loc is not None:
            return loc[1]
        return None

    def get_filename(self, section, option):
        loc = self.get_location(section, option)
        if loc is not None:
            return loc[0]
        return None


class RawConfigParser(LineTrackingMixin, configparser.RawConfigParser):
    def __init__(self, *args, **kwargs):
        configparser.RawConfigParser.__init__(self, *args, **kwargs)
        LineTrackingMixin.__init__(self)

class ConfigParser(LineTrackingMixin, configparser.ConfigParser):
    def __init__(self, *args, **kwargs):
        configparser.ConfigParser.__init__(self, *args, **kwargs)
        LineTrackingMixin.__init__(self)

class SafeConfigParser(LineTrackingMixin, configparser.SafeConfigParser):
    def __init__(self, *args, **kwargs):
        configparser.SafeConfigParser.__init__(self, *args, **kwargs)
        LineTrackingMixin.__init__(self)

