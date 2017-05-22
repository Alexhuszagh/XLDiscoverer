'''
    Objects/Abstract/sequence
    _________________________

    Functions shared between sequence objects as well
    as sequence utilities.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.utils import serialization

__all__ = [
    'from_args',
    'from_list',
    'serializable',
    'to_list',
    'uniquer',
]

# UNIQUER
# -------


def uniquer(seq, idfun=None):
    '''
    Convert sequence to a unique list while keeping order.
    Recipe modified from:
    https://code.activestate.com/recipes/52560-remove-duplicates-from-a-sequence/
    :
        >>> uniquer(range(4) + range(-2, 4))
        [0, 1, 2, 3, -2, -1]
    '''

    if idfun is None:
        def idfun(var):
            return var
    seen = set()
    result = []

    for item in seq:
        marker = idfun(item)
        if marker not in seen:
            seen.add(marker)
            result.append(item)
    return result


# SERIALIZER
# ----------


@serialization.tojson
def to_list(self):
    '''
    Serialize data for object reconstruction to JSON. Uses a `list`
    representation to serialize the data.

    Return (list): serialized data
    '''

    return list(self)


def from_args(cls, data):
    '''
    Deserialize JSON data into object constructor. Uses `*args` to
    deserialize the data, similar to the constructors for namedtuples
    and namedlists.

    Args:
        data (list):   serialized object data
    Returns (object):  class instance
    '''

    return cls(*data)


def from_list(cls, data):
    '''
    Deserialize JSON data into object constructor. Uses a single `list`
    type object to deserialize the data, similar to the constructor
    for lists and subclasses lists.

    Args:
        data (list):   serialized object data
    Returns (object):  class instance
    '''

    return cls(data)


def serializable(name, serialize=to_list, deserialize=from_args):
    '''Add serialization methods to a named sequence'''

    def decorator(cls):
        '''Add serialization methods to class'''

        registered = serialization.register(name)(cls)
        registered.__json__ = serialize
        registered.loadjson = classmethod(deserialize)
        return registered

    return decorator
