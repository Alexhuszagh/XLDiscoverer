'''
    Unittests/General/Mapping/functions
    ___________________________________

    Test suite for shared functions between mapping objects.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import json
import os
import unittest

from collections import namedtuple

from namedlist import namedlist

import numpy as np

from xldlib.general.mapping import functions, serialize
from xldlib.utils.io_ import high_level


# OBJECTS
# -------

JsonTest = namedlist("JsonTest", "input output")
NamedList = namedlist("NamedList", "field")
NamedTuple = namedtuple("NamedTuple", "field")


class Unserializable(object):
    '''Unserializable object definition'''


class NoSetter(dict):
    '''Dictionary object with an optionally blocked `__setitem__` method'''

    # BLOCKED
    # -------
    blocked = False

    #     MAGIC

    def __setitem__(self, key, value):
        '''Set dict key to value, equivalent to self[key] = value'''

        if self.blocked:
            raise NotImplementedError
        else:
            super(NoSetter, self).__setitem__(key, value)

    #     PUBLIC

    update = functions.update_setitem


@functions.serializable('Dict')
class Dict(dict):
    '''Custom dict with serialization methods'''


# ITEMS
# -----

ITEMS = [
    JsonTest(input=1,
        output="1"),
    JsonTest(input=np.int64(1),
        output="1"),
    JsonTest(input=np.int32(1),
        output="1"),
    JsonTest(input=np.float32(1),
        output="1.0"),
    JsonTest(input=np.float64(1),
        output="1.0"),
    JsonTest(input=np.False_,
        output="false"),
    JsonTest(input=np.True_,
        output="true"),
    JsonTest(input=np.nan,
        output="NaN"),
    JsonTest(input=b'',
        output='""'),
    JsonTest(input=[1],
        output='[1]'),
    JsonTest(input=(1,),
        output='[1]'),
    JsonTest(input={1: 3},
        output='{"1": 3}'),
    JsonTest(input={1},
        output='[1]'),
    JsonTest(input=NamedList(1),
        output='[1]'),
    JsonTest(input=NamedTuple(1),
        output='[1]'),
    JsonTest(input=Unserializable,
        output=TypeError),
    JsonTest(input=Unserializable(),
        output=TypeError),
]


# CASES
# -----


class NamedTest(unittest.TestCase):
    '''Test named sequences'''

    def test_dict(self):
        '''Test serialization methods for namedtuple instances'''

        values = Dict({i: i**2 for i in range(10)})
        self.assertTrue(Dict.loadjson(values.__json__()))


class SerializerTest(unittest.TestCase):
    '''Tests custom `default` keyword provided to a JSON serializer'''

    #     TESTS

    def test_objects(self):
        '''Test serialization of various python objects'''

        for item in ITEMS:
            self._test_dumps(item)

    #   NON-PUBLIC

    def _test_dumps(self, item):
        '''
        Test serialization of a custom or builtin data type

        Args:
            item (object):  item to serialize
        '''

        if hasattr(item.output, "args"):
            with self.assertRaises(item.output):
                json.dumps(item.input, default=functions.tojson)
        else:
            value = json.dumps(item.input, default=functions.tojson)
            self.assertEquals(value, item.output)


class MappingFunctionsTest(unittest.TestCase):
    '''Tests for functions (unbound methods) shared between mapping objects'''

    def setUp(self):
        '''Set up unittests'''

        self.dict = NoSetter()

        self.serializable = serialize.IoMapping()
        self.serializable.path = high_level.mkstemp()

        self.changeable = serialize.IoMapping()
        self.changeable.path = high_level.mkstemp()
        self.changeable.changed = {}

    def test_update(self):
        '''Test `update_setitem calls `__setitem__`'''

        self.dict.update({1: 3})
        self.assertEquals(self.dict, {1: 3})

        self.dict.update([(2, 4)])
        self.assertEquals(self.dict, {1: 3, 2: 4})

        self.dict.blocked = True
        with self.assertRaises(NotImplementedError):
            self.dict[1] = 3

        with self.assertRaises(NotImplementedError):
            self.dict.update({1: 3})

    def test_save(self):
        '''Test dumping object to `object.path`'''

        self.serializable[1] = 3
        functions.save(self.serializable)

        document = functions.load_document(self.serializable)
        self.assertEquals(document, {u'1': 3})

    def test_save_changed(self):
        '''Test dumping only changed values to `object.path`'''

        self.changeable.changed[1] = 3
        functions.save_changed(self.changeable)

        document = functions.load_document(self.changeable)
        self.assertEquals(document, {u'1': 3})

    def tearDown(self):
        '''Tear down unittests'''

        os.remove(self.serializable.path)
        os.remove(self.changeable.path)

        del self.dict, self.serializable, self.changeable

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(NamedTest('test_dict'))
    suite.addTest(SerializerTest('test_objects'))
    suite.addTest(MappingFunctionsTest('test_update'))
    suite.addTest(MappingFunctionsTest('test_save'))
    suite.addTest(MappingFunctionsTest('test_save_changed'))
