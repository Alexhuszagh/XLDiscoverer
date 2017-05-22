'''
    General/Mapping/frozen
    ______________________

    Immutable mapping data object definitions (columns) containing llists
    of sequential values (rows).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import Mapping, OrderedDict

from xldlib.general import sequence
from xldlib.utils import serialization

from .table import TableModelMixin


__all__ = [
    'FrozenTable',
    'TableModel'
]

# OBJECTS
# -------


class FrozenTable(OrderedDict):
    '''
    Nearly immutable OrderedDict with a list per-key, producing a
    table-like object with O(1) item lookups.

    `__setitem__` has been modified, allowing replacement of columns
    with new input data, while other methods (`update`, `clear`, ...)
    have been blocked.
    '''

    def __init__(self, attrs, visible=None):
        self.attrs = OrderedDict()
        super(FrozenTable, self).__init__()

        if visible is None:
            visible = self.attrs
        self._visible = visible
        self.__update(attrs)
        self._columns = list(self._visible)
        self._list = [self[i] for i in self._visible.values()]

    #    PROPERTIES

    @property
    def blocked(self):
        raise NotImplementedError

    __delitem__ = clear = update = blocked
    pop = popitem = setdefault = blocked

    @property
    def visible(self):
        return self._visible

    #     MAGIC

    def __setitem__(self, key, value):
        '''
        Set value if key in self (column-swap), else, block access
        See `__setitem` for full arg specs.
        '''

        if key in self:
            self._setitem(key, value)
        else:
            self.blocked()

    def __getattr__(self, name):
        '''
        Override __getattr__ to provide convenient a.x access to columns
        by column attribute names, otherwise, return class/instance
        variable.

        Args:
            name (str):  attribute name for column or class
        '''

        # do not use hasattr, as it calls `getattr`
        if self.__dict__.get('attrs') and name in self.attrs:
            key = self.attrs[name]
            return self[key]
        else:
            return super(FrozenTable, self).__getattribute__(name)

    #    NON-PUBLIC

    def __update(self, other):
        '''
        Non-public `update` method, which bypasses data integrity
        checks during initialization.

        Args:
            other (dict, iterable):  pass
        '''
        if isinstance(other, Mapping):
            for key, attr in other.items():
                self._add_column(key, attr)

        elif isinstance(other, (list, tuple)):
            for key, attr in other:
                self._add_column(key, attr)

    def _setitem(self, key, value, dict_setitem=OrderedDict.__setitem__):
        '''
        Modified, non-public, OrderedDict `__setitem__` implementation.
        Fills column with data from value

        Args:
            key (str):          column name
            value (iterable):   column data for each row
        '''

        self[key][:] = value

    def _add_column(self, key, name, dict_setitem=OrderedDict.__setitem__):
        '''
        Non-public method to add column to table.

        Args:
            key (str):          column name
            name (iterable):    attribute name for inst.name access
        '''

        dict_setitem(self, key, sequence.ExtendableList())
        self.attrs[name] = key


@serialization.register("TableModel")
class TableModel(FrozenTable, TableModelMixin):
    '''
    FrozenTable with methods and properties for implementation as a table
    model for a Qt table view.

    Includes methods for row and column access, find/replace queries,
    item deletion, and data serialization.

    TableModel supports row-wise item setting by index-based or
    name-based access.
        `TableModel.columns[index][row] = 5`
        `TableModel[name][row] = 5`
    '''

    #     MAGIC

    @serialization.tojson
    def __json__(self):
        '''
        Serialize data for object reconstruction to JSON

        Returns (dict): serialized data
        '''

        return {
            'attrs': [(k, v) for k, v in self.attrs.items()],
            'visible': [(k, v) for k, v in self.visible.items()],
            'data': dict(self)
        }

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        '''
        Deserialize JSON data into object constructor

        Args:
            data (dict, mapping):   serialized object data
        Returns (TableModel):       class instance
        '''

        attrs = data['attrs']
        visible = OrderedDict(data['visible'])
        inst = cls(attrs, visible)
        for key, value in data['data'].items():
            cls[key] = value
        return inst

    #    PROPERTIES

    @property
    def length(self):
        return max(len(i) for i in self.values())

    @property
    def rows(self):
        return range(self.length)

    @property
    def columns(self):
        return self._columns

    @property
    def row_count(self):
        return self.length

    @property
    def column_count(self):
        return len(self.columns)

    @property
    def list(self):
        return self._list

    #    PUBLIC

    def iterrows(self, columns=None, use_attrs=False):
        '''
        Row-wise iterator for table data

        Args:
            columns (None, iterable):   columns to return data from
        '''

        if columns is None and not use_attrs:
            columns = list(self)
        elif columns is None and use_attrs:
            columns = self.columns

        for row in self.rows:
            if use_attrs:
                values = (getattr(self, k)[row] for k in columns)
            else:
                values = (self[k][row] for k in columns)
            yield OrderedDict(zip(columns, values))
