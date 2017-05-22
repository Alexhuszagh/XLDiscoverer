'''
    Unittests/Utils
    _______________

    Test suite for helper functions and objects.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import bio, decorators, io_, logger, masstools, signals

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    decorators.add_tests(suite)
    bio.add_tests(suite)
    io_.add_tests(suite)
    logger.add_tests(suite)
    masstools.add_tests(suite)
    signals.add_tests(suite)
