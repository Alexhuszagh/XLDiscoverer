'''
    Unittests/Utils/signals
    _______________________

    Test suite for a simple signal/slot implementation.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.utils import signals


# OBJECTS
# -------


class Immutable(object):
    '''Test signal/slot connections for standard objects'''

    def __init__(self):
        super(Immutable, self).__init__()

        self.values = {}
        self.changed = signals.Signal()

    def store(self, key, value):
        '''Store key/value pair on a `self.changed` signal'''

        self.values[key] = value


class Mutable(dict):
    '''Test slot connections and disconnects for mutable objects'''

    def __init__(self):
        super(Mutable, self).__init__()

        self.changed = signals.Signal()

    def store(self, key, value):
        '''Store key/value pair on a `self.changed` signal'''

        self[key] = value


# CASES
# -----

class SignalsTest(unittest.TestCase):
    '''Test for a signal/slot recipe'''

    #     TESTS

    def test_immutable(self):
        '''Test signal/slot connections for immutable objects'''

        immutable = Immutable()
        self._test_object(immutable, immutable.values)

    def test_mutable(self):
        '''
        Test signal/slot connections for mutable objects. Original recipe
        uses `__self__` in a memo, which prevents mutable object connections.
        '''

        mutable = Mutable()
        self._test_object(mutable, mutable)

    #   NON-PUBLIC

    def _test_object(self, obj, store):
        '''Test for signal/slot connection via item setters'''

        obj.changed.emit('key', 'value')
        self.assertEquals(store, {})

        obj.changed.connect(obj.store)
        obj.changed.emit('key', 'value')
        self.assertEquals(store, {'key': 'value'})

        obj.changed.disconnect(obj.store)
        obj.changed.emit('newkey', 'newvalue')
        self.assertEquals(store, {'key': 'value'})


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(SignalsTest('test_immutable'))
    suite.addTest(SignalsTest('test_mutable'))
