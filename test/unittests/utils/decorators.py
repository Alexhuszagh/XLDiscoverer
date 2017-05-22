'''
    Unittests/Utils/decorators
    __________________________

    Tests for generic XL Discoverer argument decorators.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.utils import decorators


# FUNCTIONS
# ---------


def sample(arg1, arg2):
    '''Sample function which accepts `arg1` and `arg2`.'''

    return arg1 is arg2


# CASES
# -----


class DecoratorTests(unittest.TestCase):
    '''Test function argument decorators'''

    def test_accepts(self):
        '''Test function decorating with argument type enforcement'''

        f = decorators.accepts(int, int, debug=2)(sample)
        with self.assertRaises(TypeError):
            f(1, 2.0)

        self.assertFalse(f(1, 2))

    def test_returns(self):
        '''Test function decorating with return type enforcement'''

        f = decorators.returns(bool, debug=2)(sample)
        self.assertFalse(f(1, 2))

        f = decorators.returns(str, debug=2)(sample)
        with self.assertRaises(TypeError):
            f(1, 2)

    def test_casts(self):
        '''Test function decorating with argument type-casting'''

        f = decorators.cast(int, int)(sample)
        self.assertFalse(f(1, 2))
        self.assertFalse(f(1, 2.0))

        with self.assertRaises(ValueError):
            f(1, 'str')

    def test_overloaded(self):
        '''Test function overloading'''

        f = decorators.overloaded(sample)
        self.assertTrue(f(1, 1, 5))
        self.assertFalse(f(1, 2))

    def test_underloaded(self):
        '''Test function underloading'''

        f = decorators.underloaded(sample)
        self.assertIsNone(f(1))
        self.assertFalse(f(1, 2))


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(DecoratorTests('test_accepts'))
    suite.addTest(DecoratorTests('test_returns'))
    suite.addTest(DecoratorTests('test_casts'))
    suite.addTest(DecoratorTests('test_overloaded'))
    suite.addTest(DecoratorTests('test_underloaded'))
