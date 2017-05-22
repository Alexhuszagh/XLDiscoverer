'''
    General/Mapping/functions
    _________________________

    Functions (unbound methods in Python 2.x) shared between
    mapping objects.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os

import numpy as np

import six

from xldlib.definitions import Json
from xldlib.utils import serialization


__all__ = [
    'load_document',
    'save',
    'save_changed',
    'serializable',
    'tojson',
    'updatechecker',
    'update_setitem'
]

# PUBLIC
# ------


def tojson(python_object):
    '''
    Custom serializer for the JSON dumps from Python objects

    Args:
        python_object (object):   any python or python-wrapped object
    '''

    # no native support for numpy-like bools:
    #   https://bugs.python.org/issue18303
    if isinstance(python_object, np.bool_):
        return bool(python_object)

    # also no support on Python3 for numpy-like ints
    # int_ and int do not work, since specify 64 bit precision
    elif isinstance(python_object, np.integer):
        return int(python_object)

    # same thing for floats
    elif isinstance(python_object, np.floating):
        return float(python_object)

    elif six.PY3 and isinstance(python_object, bytes):
        return python_object.decode('utf-8')

    elif isinstance(python_object, set):
        return list(python_object)

    elif hasattr(python_object, "_asdict"):
        # namedlist type
        return list(python_object)

    else:
        raise TypeError("Unrecognized object {}".format(python_object))


def save_changed(self):
    '''Dump the changed JSON configurations to `self.path`'''

    if self.path is not None:
        _save(self.changed, self.path)


def save(self):
    '''Dump the JSON configurations to `self.path`'''

    if self.path is not None:
        _save(self, self.path)


def load_document(self):
    '''
    Load object data from `self.path`

    Returns (dict): stored object data
    '''

    if self.path is not None and os.path.exists(self.path):
        with open(self.path, "r") as loads:
            document = Json.load(loads)
        return document


def update_setitem(self, *args, **kwds):
    '''
    Update conf from dict/iterable in `*args` and keyword
    arguments in `**kwds`,

    Uses `__setitem__` to allow any method overrides to identify
    mapping data changes.
    '''

    updatechecker(self, args, kwds)
    # Make progressively weaker assumptions about "other"
    other = ()
    if len(args) == 1:
        other = args[0]

    if isinstance(other, dict):
        _pairwise_iterator(self, other.items())
    elif hasattr(other, "keys"):
        _single_iterator(self, other, other.keys())
    else:
        _pairwise_iterator(self, other)

    _pairwise_iterator(self, kwds.items())


def updatechecker(self, args, kwds):
    '''Verify `self.update` has been called with suitable arguments'''

    if len(args) > 1:
        raise TypeError('update() takes at most 2 positional '
                        'arguments (%d given)' % (len(args)+1,))
    elif not args and not kwds:
       raise TypeError('update() takes at least 1 argument (0 given)')


# SERIALIZATION
# -------------


@serialization.tojson
def to_list(self):
    '''
    Serialize data for object reconstruction to JSON

    Returns (dict): serialized data
    '''

    return dict(self)


def from_dict(cls, data):
    '''
    Deserialize JSON data into object constructor

    Args:
        data (dict, mapping):   serialized object data
    Returns (object):           class instance
    '''

    return cls(data)


def serializable(name):
    '''Add serialization methods to a named sequence'''

    def decorator(cls):
        '''Add serialization methods to class'''

        registered = serialization.register(name)(cls)
        registered.__json__ = to_list
        registered.loadjson = classmethod(from_dict)
        return registered

    return decorator


# PRIVATE
# -------


def _save(obj, path):
    '''
    Serialize `obj` to JSON and dump to `path`.

    Args:
        obj (JSON-compatible):   any JSON-serializable python object
        path (str):              path to file on disk
    '''

    with open(path, "w") as dump:
        Json.dump(obj, dump, sort_keys=True, indent=4, default=tojson)


def _pairwise_iterator(self, iterable):
    '''
    Exhaust iterator containing pair-wise elements, that is,
    key-value pairs, and sequentially add items to self.

    Args:
        iterable (iterable):    iterable with 2 items per element
    '''

    for key, value in iterable:
        self[key] = value


def _single_iterator(self, other, iterable):
    '''
    Exhaust iterator containing single elements corresponding
    to object keys, and sequentially add key and other[element]
    to self.

    Args:
        iterable (iterable):    iterable with a single item per element
    '''

    for key in iterable:
        self[key] = other[key]
