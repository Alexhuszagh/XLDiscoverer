'''
    Unittests/Qt/Resources
    ______________________

    Test suite for Qt resources definitions, which namespaces and
    objects to set Qt object paramaters.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import configurations, enums, flags


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    configurations.add_tests(suite)
    enums.add_tests(suite)
    flags.add_tests(suite)
