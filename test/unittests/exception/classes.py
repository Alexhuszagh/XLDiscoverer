'''
    Unittests/Exception/classes
    ___________________________

    Unit tests for custom Exception classes.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.exception import classes


# ITEMS
# -----

CLASSES = [
    classes.ModificationError
]


# CASES
# -----


class ExceptionTest(unittest.TestCase):
    '''Test throwing and catching of custom exception classes'''

    def test_throwing(self):
        '''Test throwing custom error classes'''

        for cls in CLASSES:
            with self.assertRaises(cls):
                raise cls

    def test_catching(self):
        '''Test catching the custom error classes'''

        for cls in CLASSES:
            with self.assertRaises(cls):
                try:
                    raise cls
                except OSError:
                    pass

            try:
                raise cls
            except Exception:
                pass

            try:
                raise cls
            except cls:
                pass


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ExceptionTest('test_throwing'))
    suite.addTest(ExceptionTest('test_catching'))
