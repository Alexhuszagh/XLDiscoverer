'''
    General/Mapping/ordered
    _______________________

    Ordered dictionary recipes.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import OrderedDict

import six

__all__ = [
    'OrderedDefaultdict',
    'OrderedRecursiveDict'
]

# OBJECTS
# -------


class OrderedDefaultdict(OrderedDict):
    '''
    OrderedDict + defaultdict recipe from Martineau at StackOverflow
    http://stackoverflow.com/a/4127426
        -- see licenses/CCPL-3.0.txt for more details.
    '''

    def __init__(self, *args, **kwds):
        if not args:
            self.factory = None
        else:
            if not (args[0] is None or callable(args[0])):
                raise TypeError('first argument must be callable or None')
            self.factory = args[0]
            args = args[1:]
        super(OrderedDefaultdict, self).__init__(*args, **kwds)

    def __missing__ (self, key):
        '''Set `key` if missing and a dict factory is defined'''

        if self.factory is None:
            raise KeyError(key)
        self[key] = default = self.factory()
        return default

    def __reduce__(self):
        '''Add pickling/unpickling support'''

        args = (self.factory,) if self.factory else ()
        if six.PY2:
            return self.__class__, args, None, None, self.iteritems()
        else:
            return self.__class__, args, None, None, self.items()


class OrderedRecursiveDict(OrderedDefaultdict):
    '''
    An ordered, recursive defaultdict, which tracks insertion order,
    and provides new instances of itself as default values for keys.
    '''

    def __init__(self, *args, **kwds):
        OrderedDefaultdict.__init__(self, OrderedRecursiveDict, *args, **kwds)
