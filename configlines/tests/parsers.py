from unittest import TestCase
import configparser

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

