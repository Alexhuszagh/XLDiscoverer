'''
    General/Sequence/lookup
    _______________________

    List with a protected dict, allowing O(1) value-based lookups
    by value.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from .user import UserList

__all__ = [
    'LookupTable'
]


class LookupTable(UserList):
    '''
    List of items with an underlying dictionary which redundantly
    stores {value: index} pairs to allow O(1) item indexing using
    the lookup. All items **must** be hashable.

    Values must be unique in the list, or the lookup will fail.
    '''

    def __init__(self, *args):
        super(LookupTable, self).__init__(*args)

        self._lookup = {j: i for i, j in enumerate(self)}

    #    PROPERTIES

    @property
    def lookup(self):
        return self._lookup

    #     MAGIC

    def __setitem__(self, index, value, list_setitem=UserList.__setitem__):
        '''
        Set list at position `index` to `value`, and update
        the underlying dict model.

        If `index` is a slice, first delete all items within slice,
        then set slice.

        Args:
            index (int, slice): position to set value
        '''

        if isinstance(index, slice):
            list_setitem(self, index, value)
            self.__reindex(0)

        else:
            oldvalue = self[index]
            self.lookup.pop(oldvalue)

            self.lookup[value] = index
            list_setitem(self, index, value)

    def __delitem__(self, index, list_delitem=UserList.__delitem__):
        '''
        Delete value at `index`, and update `self._lookup`

        Args:
            index (int, slice): position to set value
        '''

        if isinstance(index, slice):
            list_delitem(self, index)
            self.__reindex(0)

        else:
            value = self[index]
            self.lookup.pop(value)
            list_delitem(self, index)
            self.__reindex(index)

    #     PUBLIC

    def append(self, value, list_append=UserList.append):
        '''
        Append value and set `value` to current length

        Args:
            value (object): new value to append to list
        '''

        self.lookup[value] = len(self)
        list_append(self, value)

    def pop(self, index=None, list_pop=UserList.pop):
        '''Remove and return `value` at `index` in self'''

        if index is None:
            index = -1
        value = list_pop(self, index)
        self.__reindex(index)

        return value

    def insert(self, index, value, list_insert=UserList.insert):
        '''Insert `value` at `index` into self'''

        value = list_insert(self, index, value)
        self.__reindex(index)

    #   NON-PUBLIC

    def __reindex(self, index):
        '''
        Reindex the lookup table from `index`

        Args:
            index (int): position of offset.
        '''

        for idx in range(index, len(self)):
            value = self[idx]
            self.lookup[value] = idx
