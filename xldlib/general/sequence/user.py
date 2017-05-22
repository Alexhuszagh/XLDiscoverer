'''
    General/Sequence/user
    _____________________

    Custom list object which returns the same subclass from operations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import copy

import six

__all__ = [
    'UserList'
]

# OBJECTS
# --------


class UserList(list):
    '''
    Subclass of list to return the custom user list for all
    magic methods, include `__add__`, `__mul__`,
    and `__getitem__` (slices only) and `__getslice__` (Python 2 only).
    '''

    #      MAGIC

    def __add__(self, other, list_add=list.__add__):
        '''Add list object to `other`'''

        return self._constructor(list_add(self, other))

    def __mul__(self, other, list_mul=list.__mul__):
        '''Multiple list object by `other`'''

        return self._constructor(list_mul(self, other))

    def __copy__(self):
        '''Shallow copy of list object'''

        return self._constructor(self)

    def __deepcopy__(self, memo={}):
        '''Deep copy of list object'''

        new = self._constructor([])
        memo[id(self)] = new
        new[:] = copy.deepcopy(tuple(self), memo)
        return new

    def __getitem__(self, index, list_getitem=list.__getitem__):
        '''Return item from `index`. For slices, return UserList(subset)'''

        if isinstance(index, slice):
            return self._constructor(list_getitem(self, index))
        else:
            return list_getitem(self, index)

    if six.PY2:
        # slice operations are deprecated in Py3.x
        def __getslice__(self, start, stop):
            return self.__getitem__(slice(start, stop))

        def __setslice__(self, start, stop, value):
            return self.__setitem__(slice(start, stop), value)

        def __delslice__(self, start, stop):
            return self.__delitem__(slice(start, stop))

        def clear(self):
            '''Clear, which clears the list, is defined in Py3.x'''

            del self[:]

    #    NON-PUBLIC

    def _constructor(self, iterable=None):
        '''
        Default list constructor class, can be subclassed to allow other
        arguments.

        Arguments:
            iterable (iterable, None):  iterable or NoneType to initialize
        '''

        cls = type(self)
        if iterable is None:
            return cls()
        else:
            return cls(iterable)
