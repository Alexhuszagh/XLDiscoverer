'''
    Chemical/Proteins/Configurations
    ________________________________

    Stored and user-editable definitions for protein and peptide
    objects.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .charges import *
from .protease import *

__all__ = [
    'ENZYMES',
    'PEPTIDE_CHARGES',
    'Protease',
    'TERMINI',
]
