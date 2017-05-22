'''
    Unittests/General/Sequence/user
    _____________________________________

    Test suite for UserList object definitions, which return subclasses
    rather than list objects for slices, etc..

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import copy
import unittest

import six

from xldlib.general.sequence import user


# OBJECTS
# -------

class Subclass(user.UserList):
    '''Subclass to demonstrate subclasses survive through operations'''


# CASES
# -----


class UserListTest(unittest.TestCase):
    '''Tests for list elongation and data access'''

    def setUp(self):
        '''Set up unittests'''

        self.initial = list(range(5))
        self.list = Subclass(self.initial)

    def test_add(self):
        '''Test `lst + other` to ensure an UserList is returned'''

        new = self.list + list(range(5, 10))
        self.assertIsInstance(new, Subclass)
        self.assertEquals(new, list(range(10)))

    def test_mul(self):
        '''Test `lst * other` to ensure an UserList is returned'''

        new = self.list * 2

        self.assertIsInstance(new, Subclass)
        self.assertEquals(new, self.initial * 2)

    def test_slice(self):
        '''Test `lst[start:end]` returns UserList subclass'''

        new = self.list[3:4]
        self.assertIsInstance(new, Subclass)
        self.assertEquals(new, self.initial[3:4])

    def test_copy(self):
        '''Test `copy.copy(lst)` returns UserList subclass'''

        new = copy.copy(self.list)
        self.assertEquals(new, self.initial)
        self.assertIsInstance(new, Subclass)

    def test_deepcopy(self):
        '''Test `copy.deepcopy(lst)` returns UserList subclass'''

        new = copy.deepcopy(self.list)
        self.assertEquals(new, self.initial)
        self.assertIsInstance(new, Subclass)

    if six.PY2:
        # test methods that are Python 2 specific

        def test_clear(self):
            '''Test list.clear is defined and works'''

            new = copy.deepcopy(self.list)
            new.clear()
            self.assertEquals(new, [])

    def tearDown(self):
        '''Tear down unittests'''

        del self.list

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(UserListTest('test_add'))
    suite.addTest(UserListTest('test_mul'))
    suite.addTest(UserListTest('test_slice'))

    if six.PY2:
        suite.addTest(UserListTest('test_clear'))
