'''
    Unittests/General/Mapping/frozen
    ________________________________

    Test suite for data tables, which have a frozen key set
    with extendable rows.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from collections import OrderedDict

from xldlib.general.mapping import frozen

# DATA
# ----

ATTRS = [
    ("MS Scans", "scans"),
    ("Matched Output", "matched")
]

VISIBLE = {
    "matched": "Matched Output"
}


# CASES
# -----


class FrozenTableTest(unittest.TestCase):
    '''Tests FrozenTable elongation and locked attribute access'''

    def setUp(self):
        '''Set up unittests'''

        self.table = frozen.FrozenTable(ATTRS)
        self.hidden = frozen.FrozenTable(ATTRS, visible=VISIBLE)

    def test_mutable(self):
        '''Test the dict is immutable for new key creation'''

        with self.assertRaises(NotImplementedError):
            del self.table['MS Scans']

        with self.assertRaises(NotImplementedError):
            self.table.clear()

        with self.assertRaises(NotImplementedError):
            self.table.update([('newkey', 'newvalue')])

        with self.assertRaises(NotImplementedError):
            self.table.pop(['MS Scans'])

        with self.assertRaises(NotImplementedError):
            self.table.popitem()

        with self.assertRaises(NotImplementedError):
            self.table.setdefault('newkey', 'newvalue')

        with self.assertRaises(NotImplementedError):
            self.table['newkey'] = 'newvalue'

    def test_attrs(self):
        '''Test attribute access for table columns'''

        self.assertEquals(self.table.scans, [])
        with self.assertRaises(AttributeError):
            self.table.random_attribute

    def test_visible(self):
        '''Test `self.visible` in comparison to `self.attr` columns'''

        self.assertEquals(self.table.visible, self.table.attrs)
        self.assertNotEquals(self.hidden.visible, self.hidden.attrs)

    def test_swap(self):
        '''Test column-swap upon re-setting a table column'''

        self.table.scans.append('')
        object_id = id(self.table.scans)
        self.assertEquals(self.table.scans, [''])

        self.table['MS Scans'] = new_data = ['New', 'data']
        self.assertEquals(self.table.scans, new_data)
        self.assertEquals(object_id, id(self.table.scans))

        del self.table.scans[:]

    def tearDown(self):
        '''Tear down unittests'''

        del self.table, self.hidden


class TableModelTest(unittest.TestCase):
    '''Tests TableModel properties for and serialization'''

    def setUp(self):
        '''Set up unittests'''

        self.table = frozen.TableModel(ATTRS)

    def test_properties(self):
        '''Test table properties, such as length and list-access'''

        self.assertEquals(self.table.length, self.table.row_count)
        self.assertEquals(self.table.length, 0)
        self.assertEquals(self.table.column_count, 2)

        self.table.scans.append('')
        self.assertEquals(self.table.length, 1)

        self.assertEquals(self.table.rows, range(1))
        self.assertEquals(self.table.columns, ['scans', 'matched'])

        self.assertEquals(self.table.list, [[''], []])

        del self.table.scans[:]

    def test_iterrows(self):
        '''Test row-wise iterators for row-based data access'''

        self.table.scans[:] = range(20)
        self.table.matched[:] = range(20, 40)

        row = OrderedDict([('MS Scans', 0), ('Matched Output', 20)])
        self.assertEquals(next(self.table.iterrows()), row)

        row = OrderedDict([('scans', 0), ('matched', 20)])
        self.assertEquals(next(self.table.iterrows(use_attrs=True)), row)

    def tearDown(self):
        '''Tear down unittests'''

        del self.table


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(FrozenTableTest('test_mutable'))
    suite.addTest(FrozenTableTest('test_attrs'))
    suite.addTest(FrozenTableTest('test_visible'))
    suite.addTest(TableModelTest('test_properties'))
    suite.addTest(TableModelTest('test_iterrows'))
