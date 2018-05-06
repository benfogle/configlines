from unittest import TestCase
import sys

import six
from six.moves import configparser
from pkg_resources import resource_filename

import configlines

class ConfigTest(TestCase):
    def test_simple(self):
        cfg = configlines.ConfigParser()
        path = resource_filename(__name__, 'data1.cfg')
        cfg.read(path)

        self.assertEqual(cfg.get('foo', 'bar'), '1')
        self.assertEqual(cfg.get_location('foo', 'bar'), (path, 2))
        self.assertEqual(cfg.get_filename('foo', 'bar'), path)
        self.assertEqual(cfg.get_line('foo', 'bar'), 2)

        self.assertEqual(cfg.get('foo', 'baz'), '2')
        self.assertEqual(cfg.get_location('foo', 'baz'), (path, 3))
        self.assertEqual(cfg.get_filename('foo', 'baz'), path)
        self.assertEqual(cfg.get_line('foo', 'baz'), 3)

        self.assertEqual(cfg.get('qwerty', 'abc'), 'a split\nline')
        self.assertEqual(cfg.get_location('qwerty', 'abc'), (path, 11))
        self.assertEqual(cfg.get_filename('qwerty', 'abc'), path)
        self.assertEqual(cfg.get_line('qwerty', 'abc'), 11)

    def test_reassign(self):
        cfg = configlines.ConfigParser()
        path = resource_filename(__name__, 'data1.cfg')
        cfg.read(path)

        self.assertEqual(cfg.get('foo', 'bar'), '1')
        self.assertEqual(cfg.get_location('foo', 'bar'), (path, 2))
        self.assertEqual(cfg.get_filename('foo', 'bar'), path)
        self.assertEqual(cfg.get_line('foo', 'bar'), 2)

        cfg.set('foo', 'bar', 'q')
        self.assertEqual(cfg.get('foo', 'bar'), 'q')
        self.assertIsNone(cfg.get_location('foo', 'bar'))
        self.assertIsNone(cfg.get_filename('foo', 'bar'))
        self.assertIsNone(cfg.get_line('foo', 'bar'))

        if sys.hexversion >= 0x03020000:
            cfg['foo']['baz'] = 'q'
            self.assertEqual(cfg.get('foo', 'baz'), 'q')
            self.assertIsNone(cfg.get_location('foo', 'baz'))
            self.assertIsNone(cfg.get_filename('foo', 'baz'))
            self.assertIsNone(cfg.get_line('foo', 'baz'))

            cfg.read_dict({'qwerty':{'abc':'a', 'def':'b'}})
            self.assertEqual(cfg.get('qwerty', 'abc'), 'a')
            self.assertIsNone(cfg.get_location('qwerty', 'abc'))
            self.assertIsNone(cfg.get_filename('qwerty', 'abc'))
            self.assertIsNone(cfg.get_line('qwerty', 'abc'))

            self.assertEqual(cfg.get('qwerty', 'def'), 'b')
            self.assertIsNone(cfg.get_location('qwerty', 'def'))
            self.assertIsNone(cfg.get_filename('qwerty', 'def'))
            self.assertIsNone(cfg.get_line('qwerty', 'def'))

    def test_defaults(self):
        cfg = configlines.ConfigParser()
        path = resource_filename(__name__, 'data2.cfg')
        cfg.read(path)

        self.assertEqual(cfg.get('sectA', 'foo'), '1')
        self.assertEqual(cfg.get_location('sectA', 'foo'), (path, 2))
        self.assertEqual(cfg.get_filename('sectA', 'foo'), path)
        self.assertEqual(cfg.get_line('sectA', 'foo'), 2)

        self.assertEqual(cfg.get('sectA', 'bar'), 'B')
        self.assertEqual(cfg.get_location('sectA', 'bar'), (path, 9))
        self.assertEqual(cfg.get_filename('sectA', 'bar'), path)
        self.assertEqual(cfg.get_line('sectA', 'bar'), 9)

        self.assertEqual(cfg.get('sectB', 'foo'), 'A')
        self.assertEqual(cfg.get_location('sectB', 'foo'), (path, 8))
        self.assertEqual(cfg.get_filename('sectB', 'foo'), path)
        self.assertEqual(cfg.get_line('sectB', 'foo'), 8)

        self.assertEqual(cfg.get('sectB', 'bar'), '2')
        self.assertEqual(cfg.get_location('sectB', 'bar'), (path, 5))
        self.assertEqual(cfg.get_filename('sectB', 'bar'), path)
        self.assertEqual(cfg.get_line('sectB', 'bar'), 5)

    def test_multiple_files(self):
        cfg = configlines.ConfigParser()
        path1 = resource_filename(__name__, 'data2.cfg')
        path2 = resource_filename(__name__, 'data3.cfg')
        cfg.read([path1, path2])

        self.assertEqual(cfg.get('sectA', 'foo'), '1')
        self.assertEqual(cfg.get_location('sectA', 'foo'), (path1, 2))
        self.assertEqual(cfg.get_filename('sectA', 'foo'), path1)
        self.assertEqual(cfg.get_line('sectA', 'foo'), 2)

        self.assertEqual(cfg.get('sectA', 'bar'), 'B')
        self.assertEqual(cfg.get_location('sectA', 'bar'), (path1, 9))
        self.assertEqual(cfg.get_filename('sectA', 'bar'), path1)
        self.assertEqual(cfg.get_line('sectA', 'bar'), 9)

        self.assertEqual(cfg.get('sectA', 'baz'), '3')
        self.assertEqual(cfg.get_location('sectA', 'baz'), (path2, 2))
        self.assertEqual(cfg.get_filename('sectA', 'baz'), path2)
        self.assertEqual(cfg.get_line('sectA', 'baz'), 2)

    def test_explicit_location(self):
        cfg = configlines.ConfigParser()
        path = resource_filename(__name__, 'data1.cfg')
        cfg.read(path)

        self.assertEqual(cfg.get('foo', 'bar'), '1')
        self.assertEqual(cfg.get_location('foo', 'bar'), (path, 2))

        cfg.set('foo', 'bar', 'A', location='preserve')
        self.assertEqual(cfg.get('foo', 'bar'), 'A')
        self.assertEqual(cfg.get_location('foo', 'bar'), (path, 2))

        loc = ("not_real.cfg", 1234)
        cfg.set('foo', 'bar', 'B', location=loc)
        self.assertEqual(cfg.get('foo', 'bar'), 'B')
        self.assertEqual(cfg.get_location('foo', 'bar'), loc)

        with self.assertRaises(ValueError):
            cfg.set('foo', 'bar', 'C', location="a bad value")
        self.assertEqual(cfg.get('foo', 'bar'), 'B')
        self.assertEqual(cfg.get_location('foo', 'bar'), loc)

        with self.assertRaises(configparser.NoSectionError):
            cfg.set('not_here', 'bar', 'C')

        cfg.set('foo', 'bar', 'D', location=None)
        self.assertIsNone(cfg.get_location('foo', 'bar'))

    def test_set_location(self):
        cfg = configlines.ConfigParser()
        cfg.add_section('foo')
        cfg.set('foo', 'bar', 'A')
        self.assertIsNone(cfg.get_location('foo', 'bar'))

        cfg.set_location('foo', 'bar', ('a', 1))
        self.assertEqual(cfg.get_location('foo', 'bar'), ('a', 1))

        with self.assertRaises(ValueError):
            cfg.set_location('foo', 'bar', 'a bad value')
        self.assertEqual(cfg.get_location('foo', 'bar'), ('a', 1))

        cfg.set_location('foo', 'bar', None)
        self.assertIsNone(cfg.get_location('foo', 'bar'))

        with self.assertRaises(configparser.NoSectionError):
            cfg.set_location('not_here', 'bar', ('a', 1))
        with self.assertRaises(configparser.NoOptionError):
            cfg.set_location('foo', 'baz', ('a', 1))
