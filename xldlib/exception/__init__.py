'''
    Exception
    _________

    Error handling messages and custom exceptions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .classes import *
from .codes import CODES
from .grammar import convert_number
from .tools import *

__all__ = [
    'CODES',
    'convert_number',
    'except_error',
    'ModificationError',
    'silence_warning',
]
