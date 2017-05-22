'''
    Unittests/General/Sequence/defaultlist
    ______________________________________

    Test suite for an extendable list providing default values
    from a callable.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import random
import unittest

from xldlib.general.sequence import defaultlist
from xldlib.utils import serialization


# FUNCTIONS
# ---------


@serialization.register('serializable')
def serializable():
    '''Serializable function to test defaultlist serialization'''

    return random.random()


# CASES
# -----


class DefaultlistTest(unittest.TestCase):
    '''Tests for default value creation'''

    def test_extension(self):
        '''Test `__setitem__` extends list until item can be set'''

        inst = defaultlist.DefaultList(random.random)
        inst[5] = 3
        self.assertEquals(inst[5], 3)
        self.assertEquals(len(inst), 6)

        self.assertTrue(all(0 <= i <= 1 for i in inst[:5]))

    def test_serialization(self):
        '''Test data serialization via `__json__` and deserialization'''

        initial = list(range(5))
        inst = defaultlist.DefaultList(serializable, initial)

        serialized = inst.__json__()
        self.assertEquals(serialized, {
            '__name__': 'default_list',
            '__data__': {
                'data': initial,
                'class': serializable.__name__,
                'module': serializable.__module__
            }})

        loaded = inst.loadjson(serialized['__data__'])
        self.assertEquals(loaded, initial)

        loaded[7] = 2
        self.assertIsInstance(loaded[6], float)

    def test_slice(self):
        '''Test `__getitem__` for slices return an DefaultList instance'''

        inst = defaultlist.DefaultList(random.random, range(10))
        sublist = inst[5:10]
        self.assertIsInstance(sublist, defaultlist.DefaultList)
        self.assertEquals(sublist, list(range(5, 10)))


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(DefaultlistTest('test_extension'))
    suite.addTest(DefaultlistTest('test_serialization'))
    suite.addTest(DefaultlistTest('test_slice'))
