'''
    Unittests/Gui/Views/Dialogs
    ___________________________

    Test suite for QDialog definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from . import contextbar


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    contextbar.add_tests(suite)
