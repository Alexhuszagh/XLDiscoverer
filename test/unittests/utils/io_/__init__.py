'''
    Unittests/Utils/Io_
    ___________________

    Test suite for input/output helper functions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import typechecker, ziptools

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    typechecker.add_tests(suite)
    ziptools.add_tests(suite)
