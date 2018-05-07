from collections import OrderedDict, defaultdict

import six
from six.moves import configparser



class _LineTrackingMixin(object):
    # This is an internal class that patches in line tracking functionality
    # to objects derived from RawConfigParser.
    # Note: No docstring so that we don't accidentally mess up derived
    # classes' docstrings.

    def __init__(self):
        # We'll call constructors explicitly to ensure that this happens after
        # the main base class.

        self._option_lines = defaultdict(dict)

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
            # Tracks when options are added or removed, and adds or removes
            # line information as appropriate.

            def __init__(inner, *args, **kwargs):
                inner.sectname = None
                dict_base.__init__(inner, *args, **kwargs)

            def __setitem__(inner, key, value):
                sectname = inner.sectname
                if sectname is not None:
                    if self._curr_lineno is not None:
                        location = self._curr_filename, self._curr_lineno
                        self._option_lines[sectname][key] = location
                    elif self._curr_filename is None and sectname is not None:
                        self._option_lines[sectname].pop(key, None)
                dict_base.__setitem__(inner, key, value)

            def __delitem__(inner, key):
                dict_base.__delitem__(inner, key)
                if inner.sectname is not None:
                    self._option_lines[inner.sectname].pop(key, None)

            def pop(inner, key, *args, **kwargs):
                val = dict_base.pop(inner, key, *args, **kwargs)
                if inner.sectname is not None:
                    self._option_lines[inner.sectname].pop(key, None)
                return val

        class SectionWrapper(self._dict):
            # OptionWrappers need to know their names. This wrapper class
            # ensures that they get that information when they are added.
            # Also removes line information when sections are removed
            def __setitem__(inner, key, value):
                value.sectname = key
                dict_base.__setitem__(inner, key, value)

            def __delitem__(inner, key):
                dict_base.__delitem__(inner, key)
                del self._option_lines[key]

            def pop(inner, key, *args, **kwargs):
                val = dict_base.pop(inner, key, *args, **kwargs)
                self._option_lines.pop(key, None)
                return val

        class FpWrapper(object):
            # A simple wrapper to track line numbers as files are read.
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

    def _read(self, fp, fpname):
        self._curr_filename = fpname
        fp = self._fp_wrapper(fp)
        try:
            super(_LineTrackingMixin, self)._read(fp, fpname)
        finally:
            self._curr_filename = None
            self._curr_lineno = None

    def get_location(self, section, option):
        """Get location information for an option value in a given section.

        Returns a tuple (filename, line_number) if location information
        exists, and None otherwise.
        """

        if not self.has_section(section):
            raise configparser.NoSectionError(section)
        elif not self.has_option(section, option):
            raise configparser.NoOptionError(option, section)
        option = self.optionxform(option)
        loc = self._option_lines[section].get(option)
        if loc is None and option in self._defaults:
            return self._option_lines[configparser.DEFAULTSECT].get(option)
        return loc

    def get_line(self, section, option):
        """Get the line number for an option value in a given section.

        Returns the line number if location information exists, and None
        otherwise.
        """

        loc = self.get_location(section, option)
        if loc is not None:
            return loc[1]
        return None

    def get_filename(self, section, option):
        """Get the file name for an option value in a given section.

        Returns the file name if location information exists, and None
        otherwise.
        """
        loc = self.get_location(section, option)
        if loc is not None:
            return loc[0]
        return None

    def set(self, section, option, value, *args, **kwargs):
        """Works like set() as documented in the configparser module, with
        the following optional keyword-only argument:

        If `location' is provided, it must be None, a tuple consiting of
        (filename, line_number), or the string 'preserve'.

        If `location' is None, (the default,) then location information will
        be erased, if present.

        If `location' is a tuple, it will be set as the new location
        information.

        If `location' is the string 'preserve', then line information will
        remain unchanged, if present.
        """

        new_location = kwargs.pop('location', None)
        if new_location not in ('preserve', None):
            try:
                filename, lineno = new_location
            except ValueError:
                err = ValueError("location must be (filename, lineno), None, "
                                 "or 'preserve'")
                six.raise_from(err, None)

        option_xform = self.optionxform(option)
        cur_location = self._option_lines[section].get(option_xform)
        super(_LineTrackingMixin, self).set(section, option, value,
                *args, **kwargs)
        if new_location == 'preserve':
            if cur_location is not None:
                self._option_lines[section][option_xform] = cur_location
        elif new_location is not None:
            self._option_lines[section][option_xform] = new_location

    def set_location(self, section, option, location):
        """Explicitly set location information for an option value in a given
        section. `location' must be a tuple of (filename, line_number).
        """

        if not self.has_section(section):
            raise configparser.NoSectionError(section)
        elif not self.has_option(section, option):
            raise configparser.NoOptionError(option, section)

        if location is not None:
            try:
                filename, lineno = location
            except ValueError:
                err = ValueError("location must be (filename, lineno) or None")
                six.raise_from(err, None)
        option = self.optionxform(option)
        self._option_lines[section][option] = location

class RawConfigParser(_LineTrackingMixin, configparser.RawConfigParser):
    def __init__(self, *args, **kwargs):
        configparser.RawConfigParser.__init__(self, *args, **kwargs)
        _LineTrackingMixin.__init__(self)

class ConfigParser(_LineTrackingMixin, configparser.ConfigParser):
    def __init__(self, *args, **kwargs):
        configparser.ConfigParser.__init__(self, *args, **kwargs)
        _LineTrackingMixin.__init__(self)

class SafeConfigParser(_LineTrackingMixin, configparser.SafeConfigParser):
    def __init__(self, *args, **kwargs):
        configparser.SafeConfigParser.__init__(self, *args, **kwargs)
        _LineTrackingMixin.__init__(self)

