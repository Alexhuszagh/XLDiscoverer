'''
    Unittests/Gui/Views/Dialogs/contextbar
    ______________________________________

    Unittests for keyboard shortcut context bars.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import random
import unittest

from PySide import QtCore, QtTest

from xldlib.gui.views.dialogs import contextbar
from xldlib.gui.views import widgets
from xldlib.qt import resources as qt


# CASES
# -----


class ShortCutWidgetTest(unittest.TestCase):
    '''Tests for the ShortCutWidget'''

    def setUp(self):
        '''Set up unittests'''

        random.shuffle(qt.TABLE_BAR)
        self.widget = contextbar.ShortCutWidget(qt.TABLE_BAR[0])

    def test_size(self):
        '''Test expected label size occurs'''

        expected = QtCore.QSize(self.widget._size, self.widget._size)
        self.assertEqual(self.widget.maximumSize(), expected)

    def tearDown(self):
        '''Tear down unittests'''

        del self.widget


class IconLabelTest(unittest.TestCase):
    '''Tests for the IconLabel'''

    def setUp(self):
        '''Set up unittests'''

        random.shuffle(qt.TABLE_BAR)
        key = contextbar.KEYICONS[qt.TABLE_BAR[0].key]
        self.label = contextbar.IconLabel(key)

    def test_size(self):
        '''Test expected label size occurs'''

        expected = QtCore.QSize(self.label._size, self.label._size)
        self.assertEqual(self.label.maximumSize(), expected)

    def tearDown(self):
        '''Tear down unittests'''

        del self.label



class ContextBarTest(unittest.TestCase):
    '''Definitions for a context bar test case'''

    def setUp(self):
        '''Set up unittests'''

        contextbar.ContextBar._windowkey = 'transitions'
        self.parent = widgets.Widget()
        self.widget = contextbar.ContextBar(self.parent, qt.TABLE_BAR)

    def test_click(self):
        '''Test widget hides on mouseClick event'''

        self.widget.show()
        self.assertEquals(self.widget.isVisible(), True)

        QtTest.QTest.mouseClick(self.widget, QtCore.Qt.LeftButton)
        self.assertEquals(self.widget.isVisible(), False)

    def tearDown(self):
        '''Tear down unittests'''

        del self.widget, self.parent



# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ShortCutWidgetTest('test_size'))
    suite.addTest(IconLabelTest('test_size'))
    suite.addTest(ContextBarTest('test_click'))
