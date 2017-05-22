'''
    Unittests/General/Sequence/lookup
    _________________________________

    Test suite for a list object with value-based position lookups.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import copy
import unittest

from xldlib.general.sequence import lookup

# CASES
# -----


class LookupTableTest(unittest.TestCase):
    '''Tests for list-dict synchrony and data access'''

    def setUp(self):
        '''Set up unittests'''

        self.initial = list(range(20))
        self.list = lookup.LookupTable(self.initial)

    def test_initialization(self):
        '''Test `self.lookup` is formed when providing initialization args'''

        self.assertEquals(self.list, self.initial)
        self.assertEquals(self.list.lookup, {i: i for i in self.initial})

    def test_setitem(self):
        '''Test updating list values updates `self.lookup`'''

        new = copy.copy(self.list)
        new[0] = -1
        self.assertEquals(new, [-1] + self.list[1:])
        self.assertEquals(new.lookup[new[0]], 0)
        self.assertEquals(new.lookup[new[10]], 10)
        self.assertEquals(new.lookup[self.list[10]], 10)

    def test_delitem(self):
        '''Test removing list values updates `self.lookup`'''

        new = copy.copy(self.list)
        del new[0]

        self.assertEquals(new, self.initial[1:])
        self.assertEquals(new.lookup[new[0]], 0)
        self.assertEquals(new.lookup[self.list[1]], 0)
        self.assertEquals(new.lookup[new[10]], 10)
        self.assertEquals(new.lookup[self.list[11]], 10)

    def test_pop(self):
        '''Same test as `test_delitem`, just for pop'''

        new = copy.copy(self.list)
        new.pop(0)

        self.assertEquals(new, self.initial[1:])
        self.assertEquals(new.lookup[new[0]], 0)
        self.assertEquals(new.lookup[self.list[1]], 0)
        self.assertEquals(new.lookup[new[10]], 10)
        self.assertEquals(new.lookup[self.list[11]], 10)

    def test_insert(self):
        '''Same inserts properly shift the lookup'''

        new = copy.copy(self.list)
        new.insert(0, 10)

        self.assertEquals(new, [10] + self.initial)
        self.assertEquals(new.lookup[new[1]], 1)
        self.assertEquals(new.lookup[self.list[0]], 1)
        self.assertEquals(new.lookup[new[11]], 11)
        self.assertEquals(new.lookup[self.list[10]], 11)

    def test_getslice(self):
        '''Test `self.lookup` is formed for subslices of `self`'''

        new = self.list[3:5]
        self.assertEquals(new, self.initial[3:5])
        self.assertEquals(new, lookup.LookupTable(self.initial[3:5]))

    def test_setslice(self):
        '''Test `self.lookup` is updated for set slices of `self`'''

        new = copy.copy(self.list)
        values = list(range(20, 40))
        new[0:0] = values

        self.assertEquals(new, values + self.initial)
        self.assertEquals(new.lookup[new[0]], 0)
        self.assertEquals(new.lookup[new[30]], 30)

    def test_delslice(self):
        '''Test `self.lookup` is updated for del slices of `self`'''

        new = copy.copy(self.list)
        del new[0:10]

        self.assertEquals(new, self.initial[10:])
        self.assertEquals(new.lookup[new[0]], 0)
        self.assertEquals(new.lookup[new[9]], 9)

    def tearDown(self):
        '''Tear down unittests'''

        del self.list, self.initial

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(LookupTableTest('test_initialization'))
    suite.addTest(LookupTableTest('test_setitem'))
    suite.addTest(LookupTableTest('test_delitem'))
    suite.addTest(LookupTableTest('test_pop'))
    suite.addTest(LookupTableTest('test_insert'))
    suite.addTest(LookupTableTest('test_getslice'))
    suite.addTest(LookupTableTest('test_setslice'))
    suite.addTest(LookupTableTest('test_delslice'))
