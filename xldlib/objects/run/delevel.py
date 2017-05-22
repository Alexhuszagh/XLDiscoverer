'''
    Objects/Run/delevel
    ___________________

    Functional methods to level a product scan.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.resources.parameters import defaults

# load objects/functions
from collections import namedtuple

# DATA
# ----

SCANKEYS = [
    'ms1',
    'precursor',
    'product'
]

# OBJECTS
# -------

ScanLevels = namedtuple("ScanLevels", SCANKEYS)


# FUNCTIONS
# ---------


def getlevels(spectra):
    '''Initializes new groups and sets them for O(1) lookup as values'''

    levels = {}
    for level in SCANKEYS:
        key = defaults.DEFAULTS[level + '_scan_level']
        levels[key] = spectra.newgroup(level)
    return levels


def delevel(spectra):
    '''Separates the scan levels from a hierarchical format'''

    levels = getlevels(spectra)
    flat = spectra.getgroup('scans')
    for num, scans in flat.items():
        level = levels.get(scans.getattr('ms_level'))

        if level is not None:
            level.create_hard_link(num, scans.group)
