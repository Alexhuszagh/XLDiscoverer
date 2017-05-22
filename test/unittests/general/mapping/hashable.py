'''
    Unittests/General/Mapping/hashable
    __________________________________

    Test suite for hashable, mapping object definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.general.mapping import hashable


# CASES
# -----


class HashableMapping(unittest.TestCase):
    '''Tests for methods of an ABC on a derived class'''

    def test_mutable(self):
        '''Test hashable.HashableMapping ABC for abstract methods'''

        inst = hashable.HashableDict({1: 3})
        self.assertTrue(1 in inst)

        with self.assertRaises(KeyError):
            hashable.HashableMapping.__getitem__(inst, 1)


class HashableDict(unittest.TestCase):
    '''Tests for hashable, immutable mapping objects'''

    def test_mutable(self):
        '''Test hashable.HashableDict ABC for standard dict methods'''

        inst = hashable.HashableDict({1: 3})
        with self.assertRaises(NotImplementedError):
            inst['key'] = "value"

        with self.assertRaises(NotImplementedError):
            del inst['key']

        with self.assertRaises(NotImplementedError):
            inst.clear()

        with self.assertRaises(NotImplementedError):
            inst.update({})

        with self.assertRaises(NotImplementedError):
            inst.pop('key')

        with self.assertRaises(NotImplementedError):
            inst.popitem()

        with self.assertRaises(NotImplementedError):
            inst.setdefault('key', 'value')

        self.assertEquals(inst[1], 3)


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(HashableMapping('test_mutable'))
    suite.addTest(HashableDict('test_mutable'))
