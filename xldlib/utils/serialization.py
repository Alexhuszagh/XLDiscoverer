'''
    Utils/serialization
    ___________________

    Default serializers and unserializers for complex data types.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.

        >>> import json
        >>> json.dumps(set())
        Traceback (most recent call last):
        ...
        TypeError: set([]) is not JSON serializable

        >>> dumps = json.dumps(set(), default=encode_json)
        >>> dumps
        '{"__data__": [], "__builtin__": "set"}'

        >>> json.loads(dumps)
        {u'__data__': [], u'__builtin__': u'set'}
        >>> json.loads(dumps, object_hook=decode_json)
        set([])
'''

# load modules
import ast
import importlib
import json
import pickle
import os
import six

import numpy as np

from xldlib.definitions import re

# load objects/functions
from collections import defaultdict


# CONSTANTS
# ---------

HEADER_CHARACTERS = 3

# REGEXP
# ------

FIRST_CAP = re.compile('(.)([A-Z][a-z]+)')
ALL_CAP = re.compile('([a-z0-9])([A-Z])')


# REGISTER
# --------
# Item register to avoid malicious, external script execution

REGISTER = defaultdict(set)
NAME_REGISTER = {}

# DATA
#----


BUILTINS = {
    'frozenset': frozenset,
    'set': set,
    'tuple': tuple,
    'dict': dict
}


# HELPERS
# -------


def convert(name):
    return ALL_CAP.sub(r'\1_\2', FIRST_CAP.sub(r'\1_\2', name)).lower()


# DECORATORS
# ----------


def register(name):
    '''Class register for security, to avoid malicious code execution'''

    def decorator(cls):
        cls._registeredname = name
        REGISTER[cls.__module__].add(cls.__name__)
        converted = convert(name)
        assert converted not in NAME_REGISTER
        NAME_REGISTER[converted] = (cls.__module__, cls.__name__)

        return cls

    return decorator


def tojson(f):
    '''Serialize an object with the module and class.'''

    def decorator(self, *args, **kwds):
        result = f(self, *args, **kwds)

        return {
            '__name__': convert(self._registeredname),
            '__data__': result
        }

    decorator.__name__ = f.__name__
    return decorator


# ENCODING/DECODING
# -----------------

# JSON
# ----


def encode_json(obj, keys=False):
    '''Custom encoding for JSON serialization'''

    if hasattr(obj, "__json__"):
        data = obj.__json__()
        data['__data__'] = encode_json(data['__data__'])
        return data

    elif isinstance(obj, frozenset):
        return {'__data__': [encode_json(i) for i in obj],
                '__builtin__': 'frozenset'}

    elif isinstance(obj, set):
        return {'__data__': [encode_json(i) for i in obj],
                '__builtin__': 'set'}

    elif isinstance(obj, tuple) and keys:
        return '__tuple__: ' + str(obj)

    elif isinstance(obj, tuple):
        return {'__data__': [encode_json(i) for i in obj],
                '__builtin__': 'tuple'}

    elif isinstance(obj, list):
        return [encode_json(i) for i in obj]

    elif isinstance(obj, dict):
        return {encode_json(k, True): encode_json(v) for k, v in obj.items()}

    # no native support for numpy-like bools:
    #   https://bugs.python.org/issue18303
    elif isinstance(obj, np.bool_):
        return bool(obj)

    # also no support on Python3 for numpy-like ints
    # int_ and int do not work, since specify 64 bit precision
    elif isinstance(obj, np.integer):
        return int(obj)

    # same thing for floats
    elif isinstance(obj, np.floating):
        return float(obj)

    elif six.PY3 and isinstance(obj, bytes):
        return obj.decode('utf-8')

    return obj


def decode_json(obj):
    '''Custom decoding for JSON unpacking'''

    if isinstance(obj, six.string_types) and obj.startswith('__tuple__: '):
        return ast.literal_eval(obj[11:])

    if '__name__' in obj:
        # by forcing only known objects (those in xldlib), it lessens
        # the use of dangerous builtins (subprocess, os, shutil), and
        # would require only access via predefined builtins
        # (dict, set, frozenset, etc.)
        msg = "Unsafe item detected: {}" .format(obj['__name__'])
        assert obj['__name__'] in NAME_REGISTER, msg

        module, name = NAME_REGISTER[obj['__name__']]
        module = importlib.import_module(module)
        cls = getattr(module, name)
        return cls.loadjson(obj['__data__'])

    elif '__builtin__' in obj:
        cls = BUILTINS[obj['__builtin__']]
        return cls(obj['__data__'])

    return obj


# I/O
# ---

# SERIALIZE
# ---------


def serialize_pickle(obj, path):
    '''
    Insecure, fast serialization protocol. Based on the built-in pickle
    for fast I/O times and guaranteed, stable compliance.

    DO NOT USE WITH UNTRUSTED DATA
        https://blog.nelhage.com/2011/03/exploiting-pickle/
    '''

    with open(path, 'wb') as f:
        f.write(b'pkl')
        pickle.dump(obj, f)


def serialize_json(obj, path):
    '''
    Ideally secure JSON-serialization method, which only specifies defined
    classes. By defining specific classes to serialize and deserialize,
    it avoids the security issues of jsonpickle, but by using JSON grammar,
    avoids the extremely long I/O times for Yaml with large data.
    '''

    with open(path, 'w') as f:
        serializable = encode_json(obj)
        f.write('jsn')
        json.dump(serializable, f)


def serialize(obj, path, pickling):
    '''Serialize an object to pickle or my safe, JSON implementation'''

    tmp_path = path + '.swp'
    if pickling:
        serialize_pickle(obj, tmp_path)
    else:
        serialize_json(obj, tmp_path)
    # finally, no errors, exchange the swp with the real file
    os.rename(tmp_path, path)


# DESERIALIZE
# -----------


def deserialize_pickle(path):
    '''Insecure pickle-based deserialization method.'''

    with open(path, 'rb') as f:
        f.read(HEADER_CHARACTERS)
        return pickle.load(f)


def deserialize_json(path):
    '''Ideally secure class-based JSON-deserialization method.'''

    with open(path, 'r') as f:
        f.read(HEADER_CHARACTERS)
        return json.load(f, object_hook=decode_json)


def deserialize(path, pickling):
    '''De-serializes an object from pickle or a JSON-based implementation'''

    assert os.path.exists(path)

    with open(path, 'rb') as f:
        header = f.read(HEADER_CHARACTERS)

    if header == b'pkl' and pickling:
        return deserialize_pickle(path)
    elif header == b'pkl':
        raise OSError("Pickling file entered but pickling is not enabled")
    else:
        return deserialize_json(path)


# TESTING
# -------

if __name__ == '__main__':
    import doctest
    doctest.testmod()
