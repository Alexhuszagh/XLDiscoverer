'''
    Unittests/XlPy/Tools/Xic_Picking
    ________________________________

    Test suite for XIC peak picking tools.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import fit


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    fit.add_tests(suite)
