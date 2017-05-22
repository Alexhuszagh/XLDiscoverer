'''
    Chemical/Proteins/Configurations/charges
    ________________________________________

    Definitions for peptide charges during spectral matching.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os

from xldlib.general import mapping
from xldlib.resources import paths


__all__ = [
    'PEPTIDE_CHARGES'
]


# PATHS
# -----
CHARGE_PATH = os.path.join(paths.DIRS['data'], 'charges.json')


# DATA
# ----

PEPTIDE_CHARGES = mapping.Configurations(CHARGE_PATH, [
    (0, (1,)),
    (1, (2,)),
    (2, (3,)),
    (3, (4,)),
    (4, (5,)),
    (5, (1, 2, 3)),
    (6, (2, 3)),
    (7, (1, 2, 3, 4)),
    (8, (2, 3, 4)),
    (9, (1, 2, 3, 4, 5)),
    (10, (2, 3, 4, 5)),
    (11, (1, 2, 3, 4, 5, 6)),
    (12, (1, 2, 3, 4, 5, 6, 7)),
])
