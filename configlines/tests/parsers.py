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

