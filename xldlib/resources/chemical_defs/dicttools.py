'''
    Resources/Chemical_Defs/dicttools
    _________________________________

    Objects for facilitated post-translational modification storing.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import six

from xldlib.definitions import Json
from xldlib.general import mapping
from xldlib.utils import serialization

# load objects/functions
from collections import defaultdict, Mapping


# OBJECTS
# --------


@serialization.register('SequentialStorage')
class SequentialStorage(mapping.IoMapping):
    '''Stores abritrary data with sequential primary keys'''

    # UPDATER
    # -------
    __update = dict.update
    loader = mapping.IoMapping.ioload

    def __init__(self, path, defaults):
        super(SequentialStorage, self).__init__()

        self.__update(defaults)
        self.path = path
        self.changed = {}

    #    MAGIC

    @serialization.tojson
    def __json__(self):
        return {
            'path': None,
            'defaults': dict(self)
        }

    def __iter__(self, dict_iter=dict.__iter__):
        '''Custom implementation that returns a sorted key list'''

        return iter(sorted(dict_iter(self)))

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        return cls(**data)

    #    PUBLIC

    def pop(self, key, default=None, dict_pop=dict.pop, reindex=True):
        '''si.pop(key, [d]) -> del ldk[key], return value'''

        try:
            value = self[key]
            self.__delitem__(key, reindex=reindex)
            return value

        except KeyError:
            if default is not None:
                return default
            else:
                raise

    #    GETTERS

    def _getnewkey(self, key=None):
        '''Returns the maximum primary key within self'''

        if self:
            newkey = max(self) + 1
            if isinstance(key, six.integer_types):
                if key < newkey:
                    return key

            return newkey
        else:
            return 1

    #     PUBLIC

    update = mapping.update_setitem

    def reindex(self):
        '''Reindexes the current primary keys'''

        counter = 1
        keys = list(self)

        for key in keys:
            if key != counter:
                value = self.pop(key, reindex=False)._replace(id=counter)
                self[counter] = value

            counter += 1

    #     HELPERS

    def _keychecker(self, key, mode=0):
        '''
        Returns a suitable key for setting
            mode -- {0, 1}
                0 -- set
                1 -- del
        '''

        if mode:
            assert isinstance(key, six.integer_types)
            return key

        else:
            return self._getnewkey(key)

    #      I/O

    def save(self):
        '''Dumps the JSON configurations to file'''

        with open(self.path, "w") as dump:
            Json.dump(self.changed, dump, sort_keys=True, indent=4,
                default=mapping.tojson)


@serialization.register('StoredNames')
class StoredNames(SequentialStorage):
    '''Stores modification with sequential primary keys'''

    def __init__(self, path, defaults):
        super(StoredNames, self).__init__(path, defaults)

        self.names = defaultdict(list)
        self.__setname(defaults)

        self.loader()

    #     MAGIC

    def __getitem__(self, key, dict_getitem=dict.__getitem__):
        '''si[key] -> si[key*] -> value'''

        if isinstance(key, six.integer_types):
            return dict_getitem(self, key)

        elif isinstance(key, six.string_types):
            return self.names[key]

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        '''si[key] = value -> si[key*] = value'''

        value = self._valuechecker(value)
        key = self._keychecker(key)

        self.names[value.name].append(value.id)
        self.changed[key] = value
        dict_setitem(self, key, value)

    def __delitem__(self, key, dict_delitem=dict.__delitem__, reindex=True):
        '''si[key] -> si[key*] -> value'''

        key = self._keychecker(key, mode=1)
        value = self[key]
        self.changed.pop(key, None)

        self.names[value.name].remove(value.id)
        if not self.names[value.name]:
            del self.names[value.name]

        dict_delitem(self, key)
        if reindex:
            self.reindex()

    #    SETTERS

    def __setname(self, defaults):
        '''Sets the modification names from the defaults'''

        if isinstance(defaults, Mapping):
            for value in defaults.values():
                self.names[value.name].append(value.id)

        elif isinstance(defaults, list):
            for key, value in defaults:
                self.names[value.name].append(value.id)
