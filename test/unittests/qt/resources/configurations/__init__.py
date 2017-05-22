'''
    Unittests/Qt/Resources/Configurations
    _____________________________________

    Test suite for Qt configurations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import rendering, views


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    rendering.add_tests(suite)
    views.add_tests(suite)
