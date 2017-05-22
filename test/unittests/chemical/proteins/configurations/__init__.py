'''
    Unittests/Chemical/Proteins
    ___________________________

    Test suite for protein configurations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import protease


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    protease.add_tests(suite)
