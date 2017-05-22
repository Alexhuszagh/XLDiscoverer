'''
    Unittests/XlPy/Tools
    ____________________

    Test suite for the XL Discoverer utilities.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import xic_picking


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    xic_picking.add_tests(suite)
