'''
    Qt/Objects/base
    _______________

    Base class definitions shared by all objects in XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.onstart.main import APP

__all__ = [
    'view',
    'thread'
]

# DECORATORS
# ----------


def view(cls):
    '''Memoize the class instance upon the calling `_init__`'''

    return _wrapper(cls, APP.views)


def thread(cls):
    '''Weakly memoize class instance upon calling `__init__`'''

    return _wrapper(cls, APP.threads)


# PRIVATE
# -------


def _wrapper(cls, memo):
    '''Memoize the class instance in `memo` upon calling `__init__`'''

    init = cls.__init__

    def decorator(self, *args, **kwds):
        '''Memoize class name and store reference to instance'''

        memo[type(self).__name__] = self
        init(self, *args, **kwds)

    cls.__init__ = decorator
    return cls
