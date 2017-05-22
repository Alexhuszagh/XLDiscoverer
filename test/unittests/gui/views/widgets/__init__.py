'''
    Unittests/Gui/Views/Widgets
    ___________________________

    Test suite for widget definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import header

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    header.add_tests(suite)
