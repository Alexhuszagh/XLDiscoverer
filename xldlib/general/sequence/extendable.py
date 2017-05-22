'''
    General/Sequence/extendable
    ___________________________

    Heterogeneous data storage with a custom list with flexible dimensions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import functions
from .user import UserList


__all__ = [
    'ExtendableList'
]


# OBJECTS
# -------


@functions.serializable("ExtendableList", deserialize=functions.from_list)
class ExtendableList(UserList):
    '''
    Extendable list implementation, which automatically scales list
    dimensions to fit data.

    >>> data = ExtendableList()
    >>> data[5] = 3
    >>> data
    [nan, nan, nan, nan, nan, 3]

    Mapping-like methods (`setdefault`, `get`) are also defined to
    provide default values for lookups.
    '''

    def __init__(self, *args, **kwargs):
        super(ExtendableList, self).__init__(*args)

        self.blank = kwargs.get("blank", float('nan'))

    #      MAGIC

    def __setitem__(self, index, value, list_setitem=UserList.__setitem__):
        '''
        Set the list `value` at `index`. If the list is shorter
        than the `index` position, extend list until the operation
        can be enacted.

        Args:
            index (int, slice): position to set value
            value (object):     value to store in list
        '''

        if isinstance(index, slice):
            # Python3 removes __setslice__, so need to manually handle slices
            list_setitem(self, index, value)
        else:
            length = len(self)
            if abs(index) < length:
                list_setitem(self, index, value)
            elif index > 0:
                # expand via end 0 slice
                value = [self.blank]*(index-length) + [value]
                self[length:length] = value
            else:
                # expand via 0 slice
                value = [value] + [self.blank]*(-length-index-1)
                list_setitem(self, slice(0, 0), value)

    def __reduce__(self):
        '''Pickling/unpickling support'''

        return self.__class__, (), None, iter(self)

    #     PUBLIC

    def setdefault(self, index, *args):
        '''
        Set default value of list at `index` if index is not set.
        If no value is provided, `self.blank` is used.

        Args:
            index (int):    position to set default value
            value (object): optional value to use instead of `self.blank`
        Returns (object):   value at position or default
        '''

        if index >= len(self):
            value = args[0] if args else self.blank
            self.__setitem__(index, value)
            return value
        return self[index]

    def get(self, index, default=None):
        '''
        Return value at index or default. Allows safe data access
        without prior knowledge of list size.

        Args:
            index (int):        position to fetch value
            default (object):   default value to return if out of bounds
        '''

        try:
            return self[index]
        except IndexError:
            return default
