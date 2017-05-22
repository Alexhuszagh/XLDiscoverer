'''
    General/Mapping/recursive
    _________________________

    Recursive dictionary factory which, by default, return
    instances of themselves.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.general.mapping import recursive

# CASES
# -----


class RecursiveDictTest(unittest.TestCase):
    '''Test for an recursive dictionary recipe'''

    def setUp(self):
        '''Set up unittests'''

        self.function_dict = recursive.recursive_dict()
        self.class_dict = recursive.RecursiveDict()

    #   PROPERTIES

    @property
    def dicts(self):
        return (self.function_dict, self.class_dict)

    #     TESTS

    def test_default(self):
        '''Test normal values can be assigned as well'''

        for obj in self.dicts:
            obj[3] = 1
            self.assertEquals(obj[3], 1)
            del obj[3]

    def test_factory(self):
        '''Test missing keys initialize a recursive factory'''

        for obj in self.dicts:
            self.assertIsInstance(obj[3][2][1], type(obj))
            del obj[3]

    def tearDown(self):
        '''Tear down unittests'''

        del self.function_dict, self.class_dict


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(RecursiveDictTest('test_default'))
    suite.addTest(RecursiveDictTest('test_factory'))
