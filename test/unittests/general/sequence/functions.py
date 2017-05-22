'''
    Unittests/General/Sequence/functions
    ____________________________________

    Test suite for methods shared between sequences and sequence utilities.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from collections import namedtuple

from namedlist import namedlist

from xldlib.general.sequence import functions


# OBJECTS
# -------


@functions.serializable('NamedTuple')
class NamedTuple(namedtuple("NamedTuple", "field other")):
    '''A custom namedtuple with serializable methods'''


@functions.serializable('NamedList')
class NamedList(namedlist("NamedList", "field other")):
    '''A custom namedlist with serializable methods'''


# CASES
# -----


class NamedTest(unittest.TestCase):
    '''Test named sequences'''

    def test_tuple(self):
        '''Test serialization methods for namedtuple instances'''

        values = NamedTuple("value", "other")
        self.assertTrue(NamedTuple.loadjson(values.__json__()))

    def test_list(self):
        '''Test serialization methods for namedlist instances'''

        values = NamedList("value", "other")
        self.assertTrue(NamedList.loadjson(values.__json__()))


class UniquerTest(unittest.TestCase):
    '''Test rendering sequences unique'''

    def test_hashable(self):
        '''Test rendering unique sequences with hashable items'''

        initial = list(range(20))
        new = functions.uniquer(initial)
        self.assertEquals(new, initial)

        doubled = initial * 2
        new = functions.uniquer(doubled)
        self.assertEquals(new, initial)

    def test_unhashable(self):
        '''Test uniquifying sequences with unhashable items'''

        initial = [{'1'}, ['2'], ['3'], {'1'}]
        new = functions.uniquer(initial, idfun=id)
        self.assertEquals(new, initial)

        new = functions.uniquer(initial, idfun=tuple)
        self.assertEquals(new, [{'1'}, ['2'], ['3']])

        with self.assertRaises(TypeError):
            # unhashable items need an idfun
            functions.uniquer(initial)


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(NamedTest('test_tuple'))
    suite.addTest(NamedTest('test_list'))
    suite.addTest(UniquerTest('test_hashable'))
    suite.addTest(UniquerTest('test_unhashable'))
