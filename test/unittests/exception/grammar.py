'''
    Unittests/Exception/grammar
    ___________________________

    Unit tests for grammatical agreement conversion.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from namedlist import namedlist

from xldlib.exception import grammar

# OBJECTS
# -------

Agreement = namedlist("Agreement", "word singular plural")


# ITEMS
# -----

ITEMS = [
    Agreement('bear%(-s)s', 'bear', 'bears'),
    Agreement('th%(-at)s', 'that', 'those'),
    Agreement('berr%(-y)s', 'berry', 'berries'),
]


# CASES
# -----


class GrammarTest(unittest.TestCase):
    '''Test grammar conversion during error handling'''

    def test_plural(self):
        '''Test pluralized forms of words'''

        for item in ITEMS:
            plural = grammar.convert_number(item.word, pluralize=True)
            self.assertEquals(plural, item.plural)

    def test_singular(self):
        '''Test singular forms of words'''

        for item in ITEMS:
            singular = grammar.convert_number(item.word)
            self.assertEquals(singular, item.singular)


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(GrammarTest('test_plural'))
    suite.addTest(GrammarTest('test_singular'))
