'''
    Unittests/Qt/Objects/base
    _________________________

    Test suite for base Qt object definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

import six

from PySide import QtGui

from xldlib.qt.objects import base

# CASES
# -----


class BaseObjectTest(unittest.TestCase):
    '''Tests for the underlying base object definitions'''

    def test_variables(self):
        '''Test class variables shared between all Qt objects'''

        self.assertIsInstance(base.BaseObject.app, QtGui.QApplication)
        self.assertIsInstance(base.BaseObject.desktop, QtGui.QDesktopWidget)

    def test_properties(self):
        '''Test properties shared between all instances of Qt objects'''

        inst = base.BaseObject()
        self.assertIsInstance(inst.desktop_width, six.integer_types)
        self.assertIsInstance(inst.desktop_height, six.integer_types)


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(BaseObjectTest('test_variables'))
    suite.addTest(BaseObjectTest('test_properties'))
