'''
    General/Sequence/defaultlist
    ____________________________

    List recipe with default values if not provided. Analogous to
    defaultdict.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import importlib

from xldlib.utils import serialization

from .user import UserList


__all__ = [
    'DefaultList'
]


# OBJECTS
# -------


@serialization.register('DefaultList')
class DefaultList(UserList):
    '''
    Extendable list factory from a callable, analogous to
    defaultdict.

    Author:
        jsbueno at StackOverflow
        http://stackoverflow.com/a/8749640/4131059

    Modified:
        Alex Huszagh

        -- License can be found at:
        https://creativecommons.org/licenses/by-sa/3.0/legalcode
    '''

    def __init__(self, factory, *args, **kwds):
        '''
        Args:
            factory (callable): new value factory
        '''
        if not callable(factory):
            raise TypeError("Factory must be a callable type")

        self._factory = factory
        super(DefaultList, self).__init__(*args, **kwds)

    #   NON-PUBLIC

    def _fill(self, index):
        '''
        Non-public method which fills the list until the list can
        set a value at `index`.
        dl = []; dl._fill(3) -> dl[fx, fx, fx, fx]

        Args:
            index (int, slice): position to set value
        '''

        while len(self) <= index:
            self.append(self._factory())

    #      MAGIC

    def __setitem__(self, index, value, list_setitem=UserList.__setitem__):
        '''
        Fill list and set the list `value` at `index`

        Args:
            index (int, slice): position to set value
            value (object):     value to store in list
        '''

        if isinstance(index, slice):
            list_setitem(self, index, value)
        else:
            self._fill(index)
            list_setitem(self, index, value)

    def __getitem__(self, index, list_getitem=UserList.__getitem__):
        '''
        Fill list so value exists and return value at `index`.

        Args:
            index (int, slice): position to set value
        '''

        if isinstance(index, slice):
            return list_getitem(self, index)
        else:
            self._fill(index)
            return list_getitem(self, index)

    @serialization.tojson
    def __json__(self):
        '''
        Serialize data for object reconstruction to JSON

        Returns (dict): factory data and serialized data
        '''

        return {
            'module': self._factory.__module__,
            'class': self._factory.__name__,
            'data': list(self)
        }

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        '''
        Deserialize JSON data into object constructor

        Args:
            data (mapping):       serialized object data
        Returns (DefaultList):    class instance
        '''

        '''Load from store safely, only if the class is registered'''

        if data['class'] in serialization.REGISTER[data['module']]:
            module = importlib.import_module(data['module'])
            factory = getattr(module, data['class'])
            return cls(factory, data['data'])

    #    NON-PUBLIC

    def _constructor(self, iterable=None):
        '''
        Override to provide self._factory
        See `UserList._constructor` for full arg specs.
        '''

        if iterable is None:
            return DefaultList(self._factory)
        else:
            return DefaultList(self._factory, iterable)
