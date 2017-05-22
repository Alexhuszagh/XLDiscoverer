'''
    Definitions/builtins
    ____________________

    Compatability between Python2 and 3, by normalizing builtins
    to act closely to Python 3.x.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import importlib
import itertools as it

import six

__all__ = [
    'UNICODE',
    'INPUT',
    'REIMPORT',
    'MAP',
    'ZIP',
    'BYTES',
    'NoneType'
]

# CONSTANTS
UNICODE = unicode if six.PY2 else str
INPUT = raw_input if six.PY2 else input
REIMPORT = reload if six.PY2 else importlib.reload
MAP = it.imap if six.PY2 else map
ZIP = it.izip if six.PY2 else zip
BYTES = str if six.PY2 else bytes
NoneType = type(None)
