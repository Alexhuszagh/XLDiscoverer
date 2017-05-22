'''
    Unittests/Gui/Views
    ___________________

    Test suite for view definitions, which includes QWidgets, etc.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import dialogs, widgets


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    dialogs.add_tests(suite)
    widgets.add_tests(suite)
