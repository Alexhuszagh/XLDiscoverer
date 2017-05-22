'''
    Unittests/Qt/Resources/enums
    ____________________________

    Test suite for Qt library enum definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from namedlist import namedlist

from PySide import QtCore, QtGui

from xldlib.qt.resources import enums

# OBJECTS
# -------

Test = namedlist("Test", "instance key enum")


# ITEMS
# -----

ITEMS = [
    Test(instance=enums.CONNECTION,
        key='Queued',
        enum=QtCore.Qt.QueuedConnection),
    Test(instance=enums.CURSOR,
        key='Arrow',
        enum=QtCore.Qt.ArrowCursor),
    Test(instance=enums.EDIT_TRIGGER,
        key='No',
        enum=QtGui.QAbstractItemView.NoEditTriggers),
    Test(instance=enums.KEY,
        key='Escape',
        enum=QtCore.Qt.Key_Escape),
    Test(instance=enums.MUTEX_RECURSION,
        key='Recursive',
        enum=QtCore.QMutex.Recursive),
    Test(instance=enums.SCROLLBAR,
        key='AsNeeded',
        enum=QtCore.Qt.ScrollBarAsNeeded),
    Test(instance=enums.SELECTION_BEHAVIOR,
        key='Rows',
        enum=QtGui.QAbstractItemView.SelectRows),
    Test(instance=enums.SELECTION_MODE,
        key='Single',
        enum=QtGui.QAbstractItemView.SingleSelection),
    Test(instance=enums.SELECTION_MODEL,
        key='Select',
        enum=QtGui.QItemSelectionModel.Select),
    Test(instance=enums.SIZE_POLICY,
        key='Fixed',
        enum=QtGui.QSizePolicy.Fixed),
    Test(instance=enums.WINDOW,
        key='NoState',
        enum=QtCore.Qt.WindowNoState),
]

# CASES
# -----


class EnumsTest(unittest.TestCase):
    '''Tests for retrieving enums from PySide definitions'''

    #     TESTS

    def test_items(self):
        '''Test enum items, ensuring proper flag creation and lookup'''

        for item in ITEMS:
            self._test_enum(*item)

    #   NON-PUBLIC

    def _test_enum(self, inst, key, enum):
        '''
        Test flag lookup and enum normalization from the Enums object.

        Args:
            inst (dict):  subclass to normalize Qt enum creation
            key (str):    enum identifier
            enum (enum):  expected Qt enum
        '''

        lookup = inst[key]
        self.assertIsInstance(lookup, inst.types)
        self.assertEquals(lookup, enum)
        self.assertEquals(inst.normalize(key), lookup)


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(EnumsTest('test_items'))
