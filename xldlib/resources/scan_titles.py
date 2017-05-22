'''
    Resources/scan_titles
    _____________________

    Provides various regular expression strings to scan
    titles, which require the use of two named capture groups
    (?P<name>pattern) based on Python's modification of the Perl5
    regex extensions. These titles are scanned sequentially, so
    more specific titles should be placed before generic ones.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from namedlist import namedlist

__all__ = [
    'SCAN_TITLES'
]

# OBJECTS
# -------

ScanTitle = namedlist("ScanTitle", "vendor format distiller regexp")

# DATA
# ----

# Each regex added needs to have a <num> and a <frac>
# capture group. If the fraction is not specified, this
# can capture a null group, but the num is crucial for
# scan linking. Any other capture groups may be additionally defined.


SCAN_TITLES = [
    ScanTitle(vendor='thermo_finnigan',
        format='raw',
        distiller='DTA SuperCharge',
        regexp=r'(?P<frac>\w+)\.(?P<num>\d+)\.\d+\.\d{1,2}\.dta'),
    ScanTitle(vendor="thermo_finnigan",
        format="raw",
        distiller="PAVA",
        regexp=(r'(?:TITLE=)?Scan (?P<num>\d+) \(rt=(?P<rt>\d*\.\d*)\) '
            r'\[(?P<frac>\w+\.\w+)\]')),
]
