'''
    Unittests/General/Mapping/reverse
    _________________________________

    Test suite for reverse-able mapping object definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.general.mapping import reverse


# CASES
# -----


class ReverseMapping(unittest.TestCase):
    '''Test forward and reverse lookups'''

    def test_lookups(self):
        '''Test forward and reverse lookups'''

        inst = reverse.BidirectionalDict()
        inst[1] = 3

        self.assertEquals(inst[1], 3)
        self.assertEquals(inst(3), 1)

    def test_hashability(self):
        '''Test both key and value must be hashable'''

        inst = reverse.BidirectionalDict()
        inst[1] = 3

        with self.assertRaises(TypeError):
            inst[{1}] = 3

        with self.assertRaises(TypeError):
            inst[3] = {1}

    def test_clear(self):
        '''Test `clear` updates both forward and reverse dicts'''

        inst = reverse.BidirectionalDict()
        inst[1] = 3
        inst.clear()
        self.assertFalse(inst)
        self.assertFalse(inst.reverse)

    def test_update(self):
        '''Test `update` updates both forward and reverse dicts'''

        inst = reverse.BidirectionalDict()
        inst.update({1: 3})
        self.assertIn(1, inst)
        self.assertIn(3, inst.reverse)

    def test_popitem(self):
        '''Test `popitem` updates both forward and reverse dicts'''

        inst = reverse.BidirectionalDict()
        inst[1] = 3
        item = inst.popitem()
        self.assertFalse(inst)
        self.assertFalse(inst.reverse)
        self.assertEquals(item, (1, 3))

    def test_setdefault(self):
        '''Test `setdefault` updates both forward and reverse dicts'''

        inst = reverse.BidirectionalDict()
        value = inst.setdefault(1, 3)
        self.assertIn(1, inst)
        self.assertIn(3, inst.reverse)
        self.assertEquals(value, 3)

    def test_pop(self):
        '''Test `pop` updates both forward and reverse dicts'''

        inst = reverse.BidirectionalDict()
        inst[1] = 3
        value = inst.pop(1)
        self.assertFalse(inst)
        self.assertFalse(inst.reverse)
        self.assertEquals(value, 3)

    def test_serialization(self):
        '''Test serializing and deserializing data to `__json__`'''

        inst = reverse.BidirectionalDict({i: i**2 for i in range(10)})
        serialized = inst.__json__()
        deserialized = inst.loadjson(serialized['__data__'])
        self.assertEquals(deserialized, inst)

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ReverseMapping('test_lookups'))
    suite.addTest(ReverseMapping('test_hashability'))
    suite.addTest(ReverseMapping('test_clear'))
    suite.addTest(ReverseMapping('test_update'))
    suite.addTest(ReverseMapping('test_popitem'))
    suite.addTest(ReverseMapping('test_setdefault'))
    suite.addTest(ReverseMapping('test_pop'))
    suite.addTest(ReverseMapping('test_serialization'))
