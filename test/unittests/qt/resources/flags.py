'''
    Unittests/Qt/Resources/flags
    ____________________________

    Test suite for Qt library flag definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from namedlist import namedlist

from PySide import QtCore

from xldlib.qt.resources import flags

# OBJECTS
# -------

Case = namedlist("Case", "key enum")
Test = namedlist("Test", "instance single multiple")

# ITEMS
# -----

ITEMS = [
    Test(instance=flags.ALIGNMENT,
        single=Case(key='Top',
            enum=QtCore.Qt.AlignTop),
        multiple=Case(key='Justify|Top',
            enum=QtCore.Qt.AlignJustify | QtCore.Qt.AlignTop)),
    Test(instance=flags.ITEM,
        single=Case(key='Selectable',
            enum=QtCore.Qt.ItemIsSelectable),
        multiple=Case(key='Selectable|Editable',
            enum=QtCore.Qt.ItemIsSelectable | QtCore.Qt.ItemIsEditable)),
    Test(instance=flags.MODIFIER,
        single=Case(key='Shift',
            enum=QtCore.Qt.ShiftModifier),
        multiple=Case(key='Shift|Alt',
            enum=QtCore.Qt.ShiftModifier | QtCore.Qt.AltModifier)),
    Test(instance=flags.MOUSE,
        single=Case(key='Left',
            enum=QtCore.Qt.LeftButton),
        multiple=Case(key='Left|Right',
            enum=QtCore.Qt.LeftButton | QtCore.Qt.RightButton)),
    Test(instance=flags.ORIENTATION,
        single=Case(key='Horizontal',
            enum=QtCore.Qt.Horizontal),
        multiple=Case(key='Horizontal|Vertical',
            enum=QtCore.Qt.Horizontal | QtCore.Qt.Vertical)),
    Test(instance=flags.WINDOW_FLAG,
        single=Case(key='Window',
            enum=QtCore.Qt.Window),
        multiple=Case(key='Window|TitleHint',
            enum=QtCore.Qt.Window | QtCore.Qt.WindowTitleHint)),
]


# CASES
# -----


class FlagTest(unittest.TestCase):
    '''Tests for retrieving flags from PySide definitions'''

    #     TESTS

    def test_items(self):
        '''Test enum items, ensuring proper flag creation and lookup'''

        for item in ITEMS:
            self._test_case(*item)

    #   NON-PUBLIC

    def _test_case(self, inst, single, multiple):
        '''
        Test flag lookup and enum normalization from the Enums object.

        Args:
            inst (dict):     subclass to normalize Qt enum creation
            single (Case):   single flag test case
            multiple (Case): multiple flag test case
        '''

        self._test_flag(inst, *single)
        self._test_flag(inst, *multiple)

    def _test_flag(self, inst, key, flag):
        '''
        Test flag lookup and enum normalization from the Enums object.

        Args:
            inst (dict):  subclass to normalize Qt enum creation
            key (str):    enum identifier
            flag (enum):  expected Qt enum
        '''

        lookup = inst[key]
        self.assertIsInstance(lookup, inst.types)
        self.assertEquals(lookup, flag)
        self.assertEquals(inst.normalize(key), lookup)


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(FlagTest('test_items'))
