'''
    Chemical/Building_Blocks
    ________________________

    Object definitions and configurations for chemical building blocks.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .aminoacids import *
from .elements import *
from .sugars import SUGARS

MONOMERS = SUGARS.copy()

__all__ = [
    'AMINOACIDS',
    'DEUTERIUM',
    'ELEMENTS',
    'MONOMERS',
    'ONE_LETTER',
]
