'''
    Chemical/Proteins
    _________________

    Object definitions and configurations for proteins and peptides.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .configurations import *
from .enzyme import ProteolyticEnzyme
from .mass_pattern import MASS_PATTERN_LOOKUP

__all__ = [
    'ENZYMES',
    'MASS_PATTERN_LOOKUP',
    'Protease',
    'Protein',
    'ProteolyticEnzyme',
    'TERMINI',
]
