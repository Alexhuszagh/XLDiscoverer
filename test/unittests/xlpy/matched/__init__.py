'''
    Unittests/XlPy/Matched
    ______________________

    Test suite for parsing matched scan data for XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import scan_titles

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    scan_titles.add_tests(suite)
