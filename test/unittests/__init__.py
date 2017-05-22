'''
    Unittests
    _________

    Unit tests for XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import sys
sys.path.insert(0, '..')

# initialize QApplication
from xldlib.onstart import main
del main

# load tests
from . import chemical, exception, general, gui, onstart, qt, utils, xlpy


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    chemical.add_tests(suite)
    exception.add_tests(suite)
    general.add_tests(suite)
    gui.add_tests(suite)
    onstart.add_tests(suite)
    qt.add_tests(suite)
    utils.add_tests(suite)
    xlpy.add_tests(suite)
