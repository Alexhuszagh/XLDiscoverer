'''
    Unittests/General/Sequence/extendable
    _____________________________________

    Test suite for extendable, sequence object definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.general.sequence import extendable


# CASES
# -----


class ExtendableListTest(unittest.TestCase):
    '''Tests for list elongation and data access'''

    def test_get(self):
        '''Test `get` to return default when position not set'''

        inst = extendable.ExtendableList(range(20))
        self.assertEquals(inst.get(4, 'default'), 4)

        self.assertEquals(inst.get(21), None)
        self.assertEquals(inst.get(21, 'default'), 'default')

    def test_extension(self):
        '''Test `__setitem__` extends list until item can be set'''

        inst = extendable.ExtendableList()
        inst[5] = 3
        self.assertEquals(inst, [inst.blank] * 5 + [3])

        del inst[:]
        inst[-5] = 3
        self.assertEquals(inst, [3] + [inst.blank] * 4)

    def test_serialization(self):
        '''Test data serialization via `__json__` and deserialization'''

        initial = list(range(20))
        inst = extendable.ExtendableList(initial)

        serialized = inst.__json__()
        self.assertEquals(serialized, {
            '__name__': 'extendable_list',
            '__data__': initial})

        self.assertEquals(inst.loadjson(serialized['__data__']), initial)

    def test_setdefault(self):
        '''Test `setdefault` to only add when position not set'''

        initial = list(range(20))
        inst = extendable.ExtendableList(initial)

        self.assertEquals(inst.setdefault(5, 20), 5)
        self.assertEquals(inst, initial)

        self.assertEquals(inst.setdefault(30, 40), 40)
        self.assertEquals(inst, initial + [inst.blank] * 10 + [40])

    def test_slice(self):
        '''Test `__getitem__` for slices return an ExtendableList instance'''

        inst = extendable.ExtendableList(range(20))
        sublist = inst[5:10]
        self.assertIsInstance(sublist, extendable.ExtendableList)
        self.assertEquals(sublist, list(range(5, 10)))


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ExtendableListTest('test_get'))
    suite.addTest(ExtendableListTest('test_extension'))
    suite.addTest(ExtendableListTest('test_serialization'))
    suite.addTest(ExtendableListTest('test_setdefault'))
    suite.addTest(ExtendableListTest('test_slice'))
