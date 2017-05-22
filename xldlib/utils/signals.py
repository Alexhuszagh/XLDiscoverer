'''
    Utils/signals
    _____________

    A simple signal/slot implementation.

    File:    signal.py
    Author:  Thiago Marcos P. Santos
    Author:  Christopher S. Case
    Author:  David H. Bronke
    Editor:  Alex Huszagh
    Created: August 28, 2008
    Updated: December 12, 2011
    Updated: February 89, 2016
    License: MIT, see licenses/MIT.txt
'''

# load future
from __future__ import print_function

# load modules/submodules
import inspect
import weakref


# SIGNALS
# -------


class Signal(object):
    '''Signal/slot mechanism without the Qt interface'''

    def __init__(self):
        self._functions = weakref.WeakSet()
        self._methods = {}

    def __call__(self, *args, **kargs):
        '''Call connected signals and slots with `args` and `kwds`'''

        # Call handler functions
        for fun in self._functions:
            fun(*args, **kargs)

        # Call handler methods
        for (mem, fun), obj in self._methods.items():
            fun(obj, *args, **kargs)

    # Alias for Qt convience
    emit = __call__

    #   PROPERTIES

    @property
    def functions(self):
        return self._functions

    @property
    def methods(self):
        return self._methods

    #    PUBLIC

    def connect(self, slot):
        '''Connect `slot` to Signal instance'''

        if inspect.ismethod(slot):
            key = self._idkey(slot)
            if key not in self.methods:
                self.methods[key] = weakref.proxy(slot.__self__)

        else:
            self.functions.add(slot)

    def disconnect(self, slot):
        '''Disconnect `slot` from Signal instance'''

        if inspect.ismethod(slot):
            key = self._idkey(slot)
            if key in self.methods:
                del self.methods[key]
        else:
            if slot in self._functions:
                self.functions.remove(slot)

    def clear(self):
        '''Clear weakref objects'''

        self.functions.clear()
        self.methods.clear()

    #   NON-PUBLIC

    @staticmethod
    def _idkey(slot):
        '''
        Return the identifier for the slot. Uses `slot.__self__` as
        a stable identifier, since the instance method is not
        stable, but the instance identifier is.
        '''

        return (id(slot.__self__), slot.__func__)
