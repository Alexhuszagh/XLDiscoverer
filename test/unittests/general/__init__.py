'''
    Unittests/General
    _________________

    Test suite for general object definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import mapping, number, sequence


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    mapping.add_tests(suite)
    number.add_tests(suite)
    sequence.add_tests(suite)
