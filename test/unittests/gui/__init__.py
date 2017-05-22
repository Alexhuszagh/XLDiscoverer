'''
    Unittests/Gui
    _____________

    Unittests for graphical user elements of XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import views


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    views.add_tests(suite)
