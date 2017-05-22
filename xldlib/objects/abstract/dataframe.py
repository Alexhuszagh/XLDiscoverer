'''
    Objects/Abstract/dataframe
    ________________________

    Custom data holders for dataframe-like mapping types.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op
import weakref

try:
    from _abcoll import KeysView, ValuesView, ItemsView
except ImportError:
    pass
from collections import Mapping

import six

from xldlib.definitions import get_ident, ZIP
from xldlib.general import mapping, sequence
from xldlib import resources


# TRANSFORM RECIPE
# ----------------


class TransformableDict(dict):
    '''
    Contains transform keys without overriding any parent subclass
    hooks.
    '''

    _suffixes = ['A', '1']

    def __init__(self, transform):
        '''
        Sets the method by which to transform the keys using a
        column dictionary.
        :
            transform -- tuple with "mode", "table", and "digit" for
                the transform mode (comparative, quantitative, normal),
                table, for the keys, and digit for the boolean.
        '''

        self.transform = transform

    # TRANSFORMERS
    # ------------

    def key_transform(self, key, index=None):
        '''Public method for internal __keytransform__'''

        return self.__keytransform__(key, index)

    def __keytransform__(self, key, index=None):
        '''Transforms key in other to key in dict'''

        if isinstance(key, six.string_types):
            return self._transform_string(key)
        elif isinstance(key, tuple):
            return self._transform_tuple(key)

    def _transform_string(self, key):
        '''Transforms string-based key in other to key in dict'''

        # transforms if no suffix for the key
        if key in self:
            return key
        else:
            for suffix in self._suffixes:
                newkey = '{0} {1}'.format(key, suffix)
                if newkey in self:
                    return newkey
            else:
                return key

    def _transform_tuple(self, key):
        '''Transforms tuple-based key in other to key in dict'''

        if key in self:
            return key
        else:
            last = key[-1]
            for suffix in self._suffixes:
                newkey = key[:-1] + ('{0} {1}'.format(key, suffix),)
                if newkey in self:
                    return newkey
            else:
                return key

    # REVERSE TRANSFORMERS
    # --------------------

    def reverse_transform(self, other, key):
        '''Public method for internal __reverse_transform__'''

        return self.__reverse_transform__(other, key)

    def __reverse_transform__(self, other, key):
        '''Transforms key in self to key in other'''

        if isinstance(key, six.string_types):
            return self._reverse_transform_string(other, key)
        elif isinstance(key, tuple):
            return self._reverse_transform_tuple(other, key)

    def _reverse_transform_string(self, other, key):
        '''Transforms string-based key in self to key in other'''

        if key in other:
            return key
        else:
            for suffix in self._suffixes:
                ending = ' {}'.format(suffix)
                if key.endswith(ending):
                    newkey = key[: -len(ending)]
                    if newkey in other:
                        return newkey
            else:
                return key

    def _reverse_transform_tuple(self, other, key):
        '''Transforms tuple-based key in self to key in other'''

        if key in other:
            return key
        else:
            last = key[-1]
            for suffix in self._suffixes:
                ending = ' {}'.format(suffix)
                if last.endswith(ending):
                    newkey = key[:-1] + (last[: -len(ending)],)
                    if newkey in other:
                        return newkey
            else:
                return key


# ORDERED TRANSFORMABLE
# ---------------------


class OrderedTransform(TransformableDict):
    '''
    Dictionary that remembers insertion order
    An inherited dict maps keys to values.
    The inherited dict provides __getitem__, __len__, __contains__, and get.
    The remaining methods are order-aware.
    Big-O running times for all methods are the
    same as for regular dictionaries.
    '''

    index = None

    def __init__(self, *args, **kwds):
        '''
        Initialize an ordered dictionary.  Signature is the same as for
        regular dictionaries, but keyword arguments are not recommended
        because their insertion order is arbitrary.
        '''

        # call base class, pop kwds so can still use keyworded values
        try:
            self.transform = kwds.pop('transform')
        except KeyError:
            self.transform = {}
        TransformableDict.__init__(self, self.transform)

        if len(args) > 1:
            raise TypeError('expected at most 1 arguments, got %d' % len(args))
        try:
            self.__root
        except AttributeError:
            self.__root = root = []                     # sentinel node
            root[:] = [root, root, None]
            self.__map = {}
        if len(args) != 0 or len(kwds) != 0:
            self.__update(*args, **kwds)

    #       MAGIC

    def __getitem__(self, key, index=None, dict_getitem=dict.__getitem__):
        return dict_getitem(self, self.__keytransform__(key, index))

    def __setitem__(self, key, value, index=None,
                    dict_setitem=dict.__setitem__):
        '''
        od.__setitem__(i, y) <==> od[i]=y
        Setting a new item creates a new link which goes at the end of
        the linked list, and the inherited dictionary is updated with
        the new key/value pair.
        '''

        key = self.__keytransform__(key, index)
        if key not in self:
            root = self.__root
            last = root[0]
            last[1] = root[0] = self.__map[key] = [last, root, key]
        # convert key to dict
        if not isinstance(value, sequence.ExtendableList):
            value = sequence.ExtendableList(value, blank='')
        # set index to grab values
        dict_setitem(self, key, value)

    def __delitem__(self, key, index=None, dict_delitem=dict.__delitem__):
        '''
        od.__delitem__(y) <==> del od[y]
        Deleting an existing item uses self.__map to find the link which
        is then removed by updating the links in the predecessor and
        successor nodes.
        '''

        key = self.__keytransform__(key, index)
        dict_delitem(self, key)
        link_prev, link_next, key = self.__map.pop(key)
        link_prev[1] = link_next
        link_next[0] = link_prev

    #      ITERATORS

    def __iter__(self):
        '''od.__iter__() <==> iter(od)'''

        root = self.__root
        curr = root[1]
        while curr is not root:
            yield curr[2]
            curr = curr[1]

    def __reversed__(self):
        '''od.__reversed__() <==> reversed(od)'''

        root = self.__root
        curr = root[0]
        while curr is not root:
            yield curr[2]
            curr = curr[0]

    #        DEL

    def clear(self):
        'od.clear() -> None.  Remove all items from od.'
        try:
            for node in self.__map.values():
                del node[:]
            root = self.__root
            root[:] = [root, root, None]
            self.__map.clear()
        except AttributeError:
            pass
        dict.clear(self)

    def popitem(self, last=True):
        '''
        od.popitem() -> (k, v), return and remove a (key, value) pair.
        Pairs are returned in LIFO order if last is true or FIFO order
        if false.
        '''

        if not self:
            raise KeyError('dictionary is empty')
        root = self.__root
        if last:
            link = root[0]
            link_prev = link[0]
            link_prev[1] = root
            root[0] = link_prev
        else:
            link = root[1]
            link_next = link[1]
            root[1] = link_next
            link_next[0] = root
        key = link[2]
        del self.__map[key]
        value = dict.pop(self, key)
        return key, value

    # -- the following methods do not depend on the internal structure --

    #      HELPERS

    def keys(self):
        '''od.keys() -> list of keys in od'''

        return list(self)

    def values(self):
        '''od.values() -> list of values in od'''

        return [self[key] for key in self]

    def items(self):
        '''od.items() -> list of (key, value) pairs in od'''

        return [(key, self[key]) for key in self]

    def iterkeys(self):
        '''od.iterkeys() -> an iterator over the keys in od'''

        return iter(self)

    def itervalues(self):
        '''od.itervalues -> an iterator over the values in od'''

        for k in self:
            yield self[k]

    def iteritems(self):
        '''od.iteritems -> an iterator over the (key, value) items in od'''

        for k in self:
            yield (k, self[k])

    update = mapping.update_setitem
    # let subclasses override update without breaking __init__
    __update = update

    __marker = object()

    def pop(self, key, default=__marker):
        '''
        od.pop(k[,d]) -> v, remove specified key and return the
        corresponding value.
        If key is not found, d is returned if given, otherwise
        KeyError is raised.
        '''

        key = self.__keytransform__(key)
        if key in self:
            result = self[key]
            del self[key]
            return result
        if default is self.__marker:
            raise KeyError(key)
        return default

    def setdefault(self, key, default=None):
        '''
        od.setdefault(k[,d]) -> od.get(k,d), also set od[k]=d if k
        not in od.
        '''

        key = self.__keytransform__(key)
        if key in self:
            return self[key]
        self[key] = default
        return default

    def __repr__(self, _repr_running={}):
        '''od.__repr__() <==> repr(od)'''

        call_key = id(self), get_ident()
        if call_key in _repr_running:
            return '...'
        _repr_running[call_key] = 1
        try:
            if not self:
                return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, list(self.items()))
        finally:
            del _repr_running[call_key]

    def __reduce__(self):
        '''Return state information for pickling'''

        items = [[k, self[k]] for k in self]
        inst_dict = vars(self).copy()
        # ensure all instance attributes removed and reset
        for k in vars(OrderedTransform()):
            inst_dict.pop(k, None)
        # make sure instance attribute which should carry over is set
        inst_dict['transform'] = self.transform
        return (self.__class__, (items,), inst_dict)

    def copy(self):
        '''od.copy() -> a shallow copy of od'''

        return self.__class__(self, transform=self.transform)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        '''
        OD.fromkeys(S[, v]) -> New ordered dictionary with keys from S
        and values equal to v (which defaults to None).
        '''

        d = cls()
        for key in iterable:
            d[key] = value
        return d

    def __eq__(self, other):
        '''
        od.__eq__(y) <==> od==y.  Comparison to another OD is order-sensitive
        while comparison to a regular mapping is order-insensitive.
        '''
        if isinstance(other, TransformableDict):
            return len(self) == len(other) and self.items() == other.items()
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self == other

    # -- the following methods are only used in Python 2.7 --

    def viewkeys(self):
        '''
        od.viewkeys() -> a set-like object providing a view on od's
        keys.
        '''

        return KeysView(self)

    def viewvalues(self):
        '''
        od.viewvalues() -> an object providing a view on od's
        values.
        '''

        return ValuesView(self)

    def viewitems(self):
        '''
        od.viewitems() -> a set-like object providing a view on od's
        items.
        '''

        return ItemsView(self)


# LOCATION INDEXING
# -----------------


class _LocationIndexer(object):
    '''Custom Indexer used to provide 2D indexing for the DataFrameDict'''

    def __init__(self, obj):
        super(_LocationIndexer, self).__init__()
        self.obj = weakref.proxy(obj)

    #       MAGIC

    def __setitem__(self, key, value):
        '''Pandas like indexing from the dict object'''

        if type(key) is tuple:
            return self._setitem_tuple(key, value)
        else:
            return self._setitem_axis(key, value, axis=0)

    def __getitem__(self, key):
        '''Pandas like indexing from the dict object'''

        if type(key) is tuple:
            return self._getitem_tuple(key)
        else:
            return self._getitem_axis(key, axis=0)

    #      SETTERS

    def _setitem_tuple(self, key, value):
        '''
        Expands the indexer and raises an exception if an improper
        indexer is included. The key can either be length 1 or 2,
        comprising an (index,) or (index, column) pair.
        Sets row or col/row value(s).
        :
            key -- tupled key corresponding to a column/row or
                multiindexed column
            value -- value to set to cell
        '''

        if len(key) > 2:
            raise IndexError("Too many indexers")
        elif len(key) < 1:
            raise IndexError("No identified indexers")
        if len(key) == 1:
            # regular index passed as tuple (return all values at row)
            key = key[0]
            self._setitem_axis(key, value)

        else:
            # passed (row, column) pair
            row, column = key
            self.obj.__getitem__(column, index=None).__setitem__(row, value)
            # set remaining values to keep dimensions similar
            for newkey in self.obj:
                if newkey != key:
                    self.obj.__getitem__(newkey).setdefault(row)

    def _setitem_axis(self, index, value, axis=0):
        '''
        Sets an item along an axis based on either a row or index
        key. Adds each value in a list sequentially to the row if
        indexing a row.
        :
            index -- row to set the item
            value -- new value to set in row
        '''

        if axis == 0:
            # along rows
            # can't use pure duck typing here -- str is sequencable
            if isinstance(value, (list, tuple)):
                # check if len same
                assert len(value) == len(self)
                for key, val in ZIP(self.obj, value):
                    self.obj[key].__setitem__(index, val)

            elif isinstance(value, Mapping):
                for key in self.obj:
                    # reverse transform the key, in case suffix added
                    key = self.obj.reverse_transform(value, key)
                    # add series sequentially to df
                    try:
                        sublist = self.obj[key]
                        # need to set the item here, have default
                        val = value.get(key, sublist.blank)
                        sublist.__setitem__(index, val)
                    except KeyError:
                        pass
            else:
                for key in self.obj:
                    self.obj[key].__setitem__(index, value)

        elif axis == 1:
            # along columns
            self.obj.__setitem__(index, value, index=None)

    #      GETTERS

    def _getitem_tuple(self, key):
        '''
        Expands the indexer and raises an exception if an improper
        indexer is included. The key can either be length 1 or 2,
        comprising an (index,) or (index, column) pair.
        Returns row or col/row value(s).
        '''

        if len(key) > 2:
            raise IndexError("Too many indexers")
        elif len(key) < 1:
            raise IndexError("No identified indexers")
        # regular index passed as tuple (return all values at row)
        if len(key) == 1:
            key = key[0]
            return self._getitem_axis(key)
        # passed (row, column) pair
        else:
            row, column = key
            return self.obj.__getitem__(column, index=None).__getitem__(row)

    def _getitem_axis(self, key, axis=0):
        '''
        Grabs an item along an axis based on a key, which is either
        an row or column key. While indexing by rows, the key is an
        integer axis for the row, and it returns a list.
        Indexing by column is equivalent to dict.__getitem__(key).
        '''

        if axis == 0:
            # along rows
            return [v.__getitem__(key) for v in self.obj.values()]

        elif axis == 1:
            # along columns
            return self.obj.__getitem__(key, index=None)


# DATAFRAMES
# ----------


class DataFrameDict(OrderedTransform):
    '''
    Creates an indexable, locable, sortable and concatenable
    dictionary that acts like a dataframe but with faster indexing.
    '''

    def __init__(self, *args, **kwds):
        '''Sets the location indexer(s).'''

        # grab column parameter to initialize blank index
        if 'columns' in kwds:
            columns = kwds.pop('columns')
        OrderedTransform.__init__(self, *args, **kwds)
        try:
            self.set_columns(columns)
        except NameError:
            pass

        # set location indexers
        self.loc = _LocationIndexer(self)
        self.columns = self

    #  PUBLIC FUNCTIONS

    def sort(self, **kwds):
        '''Sorts the dataframe'''

        columns = kwds.get('columns', [])
        # 0 for sorting list indexes, 1 for columns (keys)
        axis = kwds.get('axis', 0)
        # grabs order keys
        ascending = kwds.get('ascending', True)
        # skip sort if no sort columns
        if columns != [] and axis == 1:
            # error message from Pandas
            raise ValueError("When sorting by column, axis must be 0 (rows)")
        # ensure sort order if designated for all columns same length
        if isinstance(ascending, (list, tuple)):
            if len(ascending) != len(columns):
                raise IndexError("Column dimensions do not match "
                                 "sort order dimensions.")
        if axis == 0:
            self.sort_index(columns, ascending)
        elif axis == 1:
            self.sort_columns(ascending)

    def concat(self, other):
        '''Concats other DataFrameDict to this one'''

        # grab key0 to determine length
        self_length = len(self[self.get_column()])
        other_length = len(other[next(iter(other))])
        # add keys currently in dict
        for key in self:
            try:
                self[key] += other[key]
            except KeyError:
                self[key] += [float('nan')]*other_length
        # add new keys
        for key in other:
            if key not in self:
                self[key] = [float('nan')]*self_length + other[key]

    def sort_index(self, columns, ascending):
        '''
        Sorts each list based on values within the index.
        Uses the zip builtin for this effect.
        :
            columns -- list of columns for sort priority
            ascending -- bool or list of bools for sort order
            self = [('a', [2, 1, 3]), ('b', [3, 4, 2])]
            sort_index(['a'], True)->[('a', [1, 2, 3]), ('b', [4, 3, 2])]
        '''

        # assert all columns in dict (including with mask)
        missing = [i for i in columns if i not in self]
        if missing:
            raise KeyError("sort keys missing from columns", ''.join(missing))
        # grab sort keys and then generate zip
        sort_keys = list(columns) + [i for i in self if i not in set(columns)]
        zipped = list(zip(*[self[i] for i in sort_keys]))
        # need to set sort depending on bool/list
        if isinstance(ascending, bool):
            zipped.sort(reverse=not ascending)
        else:
            # negative slice to sort lower ranked columns first
            for index in range(len(ascending))[::-1]:
                asc = ascending[index]
                zipped.sort(key=op.itemgetter(index), reverse=not asc)
        # now need to set to values
        values = list(zip(*zipped))
        for index, key in enumerate(sort_keys):
            value = values[index]
            self[key] = value

    def sort_columns(self, ascending):
        '''
        Sorts the column order, by resetting OrderedTransform.__root.
        Just simply replaces OrderedTransform.__root to the proper
        form.
        :
            ascending -- bool or list of bools for sort order
            sort_columns(True)->[('a', [...]), ('b', [...])]
        '''

        # grab keys
        keys = sorted(self, reverse=not ascending)
        self._change_root(keys)

    def rename(self, columns=None, **kwds):
        '''
        Renames a given key and sets it in the exact same position
        within the root.
        '''

        self._change_root(list(self), mask=columns)

    #      SETTERS

    def set_columns(self, columns, length=0):
        '''Sets the columns to initialize the DataFrame'''

        for column in columns:
            default = sequence.ExtendableList(blank='')
            default += [float('nan')] * length
            self.setdefault(column, default)

    def set_value(self, index=None, value=' '):
        '''Sets a value in the dataframe, default a row spacer'''

        column = self.get_column()
        if index is None:
            index = self.get_last_index()
        self.loc[index, column] = value

    def set_header(self):
        '''Sets the dataframe header'''

        string = 'xlDiscoverer v{0}'.format(resources.BUILD)
        self.set_value(index=0, value=string)

    #      HELPERS

    def _change_root(self, keys, **kwds):
        '''
        Changes the root order or names based on a key list, with
        optional keywords to change the column names.
        '''

        tmp = {k: self.pop(k) for k in keys}
        # blank ordered root and reset
        root = self._OrderedTransform__root
        root[:] = [root, root, None]

        # reset root using same protocol
        mask = kwds.get("mask", {})
        for key in keys:
            new_key = mask.get(key, key)
            self[new_key] = tmp[key]

    #      GETTERS

    def get_last_index(self):
        '''Grabs the last index in the current instance'''

        column = self.get_column()
        return len(self[column])

    def get_column(self, index=0):
        '''Grabs the column from index in the dataframe dict'''

        itr = iter(self)
        while index:
            next(itr)
            index -= 1
        return next(itr)
