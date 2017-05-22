'''
    Unittests/Gui/Views/Widgets/header
    __________________________________

    Test suite for widget definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from PySide import QtCore

from xldlib.gui.views.widgets import header


# CASES
# -----


class HeaderViewTest(unittest.TestCase):
    '''Tests for a custom QHeaderView object'''

    def setUp(self):
        '''Set up unittests'''

        self.horizontal = header.HeaderView('Horizontal')
        self.vertical = header.HeaderView('Vertical')

    def test_orientation(self):
        '''Test `QHeaderView` orientation upon initialization'''

        self.assertEquals(self.horizontal.orientation(), QtCore.Qt.Horizontal)
        self.assertEquals(self.vertical.orientation(), QtCore.Qt.Vertical)

    def test_resize_mode(self):
        '''Test resizeMode of QHeaderView'''

        # test both the overloaded and standard setResizeMode
        # don't test resizeMode values, since there is no model
        self.horizontal.set_resize_mode(0, 'Fixed')
        self.vertical.set_resize_mode('Interactive')

    def tearDown(self):
        '''Tear down unittests'''

        del self.horizontal, self.vertical


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(HeaderViewTest('test_orientation'))
    suite.addTest(HeaderViewTest('test_resize_mode'))
