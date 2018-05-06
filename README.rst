.. image:: https://travis-ci.org/benfogle/configlines.svg?branch=master
    :target: https://travis-ci.org/benfogle/configlines

.. image:: https://codecov.io/gh/benfogle/configlines/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/benfogle/configlines


Description
-----------
This module is an extension to Python's standard `configparser`_ module
that adds file and line number information to each stored option. This
is primarily useful in reporting error messages: you can point your user
to exactly where a bad value occurred:

.. code:: python

    try:
        timeout = config.getint('connection', 'retry')
    except ValueError:
        filename, line = config.get_location('connection', 'retry')
        logging.error("retry must be an integer (%s:%d)", filename, line)
        ...

This package is compatible with both Python 2 and 3.

Installation
------------

Install with pip::

    $ pip install configlines

Usage
-----

Given the following two configuration files:

.. code:: ini

    # Line one of data1.cfg
    [some_section]
    foo = 1

    [DEFAULT]
    bar = 2

.. code:: ini

    # Line one of data2.cfg
    [some_section]
    baz = 3

You can read and manipulate them exactly the same as the standard module:

.. code:: python

    >>> from configlines import ConfigParser
    >>> cfg = ConfigParser()
    >>> cfg.read(['data1.cfg', 'data2.cfg'])
    >>> cfg.get('some_section', 'foo')
    '1'

You can also access file and line information:

.. code:: python

    >>> cfg.get_location('some_section', 'foo')
    ('data1.cfg', 3)
    >>> cfg.get_location('some_section', 'bar')
    ('data1.cfg', 6)
    >>> cfg.get_location('some_section', 'baz')
    ('data2.cfg', 3)

In addition to ``get_location``, this module also provides ``get_line`` and
``get_filename`` functions for convenience.

If an option didn't come from a file, (i.e., you set it programmatically,) then
line number information will not be present:

.. code:: python

    >>> cfg.set('some_section', 'qwerty', '1234')
    >>> cfg.get_location('some_section', 'qwerty')
    None

Overwriting options programatically will erase line number information:

.. code:: python

    >>> cfg.get_location('some_section', 'foo')
    ('data1.cfg', 3)
    >>> cfg.set('some_section', 'foo', '1234')
    >>> cfg.get_location('some_section', 'foo')
    None

.. _configparser: https://docs.python.org/3/library/configparser.html

