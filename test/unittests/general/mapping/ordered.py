'''
    Unittests/General/Mapping/ordered
    _________________________________

    Test suite for ordered mapping object definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.general.mapping import ordered


# CASES
# -----


class OrderedDefaultdictTest(unittest.TestCase):
    '''Test for an ordered, default dict recipe'''

    def setUp(self):
        '''Set up unittests'''

        self.dict = ordered.OrderedDefaultdict(list)
        self.no_factory = ordered.OrderedDefaultdict()

    def test_default(self):
        '''Test normal values can be assigned as well'''

        self.dict[3] = 1
        self.assertEquals(self.dict[3], 1)
        del self.dict[3]

    def test_missing(self):
        '''Test missing keys initialize the factory'''

        self.assertIsInstance(self.dict[3], list)
        with self.assertRaises(KeyError):
            self.no_factory[3]

        del self.dict[3]

    def tearDown(self):
        '''Tear down unittests'''

        del self.dict


class OrderedRecursiveDictTest(unittest.TestCase):
    '''Test for a recursive, ordered, default dict recipe'''

    def setUp(self):
        '''Set up unittests'''

        self.dict = ordered.OrderedRecursiveDict()

    def test_default(self):
        '''Test normal values can be assigned as well'''

        self.dict[3] = 1
        self.assertEquals(self.dict[3], 1)
        del self.dict[3]

    def test_factory(self):
        '''Test missing keys initialize a recursive factory'''

        self.assertIsInstance(self.dict[3][2][1], ordered.OrderedRecursiveDict)
        del self.dict[3]

    def tearDown(self):
        '''Tear down unittests'''

        del self.dict


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(OrderedDefaultdictTest('test_default'))
    suite.addTest(OrderedDefaultdictTest('test_missing'))
    suite.addTest(OrderedRecursiveDictTest('test_default'))
    suite.addTest(OrderedRecursiveDictTest('test_factory'))
