'''
    General/Mapping/serialize
    _________________________

    Mapping objects for data serialization and deserialization,
    to facilitate configuration loading and saving.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import Mapping

from xldlib.utils import serialization, signals

from . import functions

__all__ = [
    'Configurations',
    'IoMapping',
]

# UPDATERS
# --------


def _update_mapping(obj, other):
    '''
    Non-public function which recursively  updates a mapping
    structure, `obj`, from an-`other` mapping object.
    It is bound as a public method in `IoMapping` and inherited
    classes.

    Args:
        obj (mapping):      object updated
        other (mapping):    data to add to obj
    '''

    for key, value in other.items():
        if isinstance(value, Mapping) and key in obj:
            _update_mapping(obj[key], value)
        else:
            obj[key] = value


# OBJECTS
# -------


@functions.serializable('IoMapping')
class IoMapping(dict):
    '''
    Mapping structure with methods for I/O operations, both for
    class reconstruction (`__json__`  and `loadjson`), as well
    as configuration storage (`ioload` and `save`).
    '''

    #     PUBLIC

    update_mapping = _update_mapping
    save = functions.save

    def ioload(self):
        '''Update object data from configurations stored at `self.path`'''

        document = self._ioload()
        if document is not None:
            self.update(document)

    #   NON-PUBLIC

    _ioload = functions.load_document


class Configurations(IoMapping):
    '''
    Mapping structure with full I/O support, and can be used for
    configuration settings.

    It loads data from `path` upon class construction,
    and dumps data via `save`. For efficiency, it keeps
    a memo of changed items `changed` and only loads/
    dumps changed values.

    To avoid type conversion, `Configurations` overrides
    `__setitem__` to cast the new value with the original
    type.
    '''

    __update = dict.update

    def __init__(self, path, defaults, new_keys=False):
        super(Configurations, self).__init__()

        self.__update(defaults)
        self.path = path
        self.new_keys = new_keys

        self.changed = {}
        self.edited = signals.Signal()

        self.ioload()

    #      MAGIC

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        '''
        Set new or changed for the mapping object and typecasts
        changed values with the original value's type.

        Args:
            key (str):      dictionary key
            value (object): data to store
        '''

        # force no new key creation
        if not self.new_keys:
            value = self._cast(key, value)

        # set the values
        self.changed[key] = value
        dict_setitem(self, key, value)

    @serialization.tojson
    def __json__(self):
        '''
        Serialize data for object reconstruction to JSON
        Returns (dict): serialized data
        '''

        return {
            'path': self.path,
            'data': dict(self),
            'changed': self.changed,
            'new_keys': self.new_keys
        }

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        '''
        Deserialize JSON data into object constructor

        Args:
            data (dict, mapping):   serialized object data
        Returns (Configurations):   class instance
        '''

        path = data['path']
        defaults = data['data']
        new_keys = data['new_keys']
        inst = cls(path, defaults, new_keys)
        inst.changed = data['changed']
        return inst

    #     PUBLIC

    update = functions.update_setitem
    save = functions.save_changed

    def modified(self, key):
        '''
        Include modified value for data serialization.

        Args:
            key (str): dictionary key
        '''

        self.changed[key] = self[key]

    #   NON-PUBLIC

    def _cast(self, key, value):
        '''
        Typecast `value` with the object type of self[key].

        Args:
            key (str):      dictionary key
            value (object): object to cast with existing type
        '''

        default = self[key]
        cast = type(default)

        if cast not in {tuple, list} and hasattr(default, "_asdict"):
            # namedtuples, namedlists
            return cast(*value)

        elif default is not None:
            return cast(value)
        return value
