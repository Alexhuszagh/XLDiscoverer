'''
    General/Mapping/table
    _____________________

    Immutable mapping data object definitions (columns) containing llists
    of sequential values (rows).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from namedlist import namedlist

from xldlib import exception

__all__ = [
    'TableModelMixin'
]

# OBJECTS
# -------

Match = namedlist("Match", "row column value number")


class TableModelMixin(object):
    '''
    Mixin class to provide find/replace, and item deletion methods
    for the underlying table model.
    '''

    # DEFAULTS
    # --------
    blank = ''

    #    PUBLIC

    def delete(self, *indexes):
        '''
        Set each value within the table model to `self.blank` from
        pointers to indexes within the model.

        Args:
            (indexes):  iterable of named objects, with row/column attributes
        '''

        if len(indexes) == 1 and isinstance(indexes[0], (list, tuple)):
            indexes = indexes[0]

        for index in indexes:
            self.list[index.column][index.row] = self.blank

    def find(self, selection, search):
        '''
        Find query string within model, with an optional selection
        to limit the index range of the search.

        Args:
            selection (object):  named object with section-wise min/max
            search (re.Pattern): compiled regex pattern for search query
        '''

        for row, column in selection.iter_cells():
            value, count = self._match(row, column, search)
            if count:
                yield Match(row, column, value, count)

    def replace(self, selection, search, replace, all_items=False):
        '''
        Find query string within model, with an optional selection
        to limit the index range of the search, and then replace
        each item with an `re` match object and replacement string.

        Args:
            selection (object):  named object with section-wise min/max
            search (re.Pattern): compiled regex pattern for search query
            replace (str):       replacement string for search query
            all_items (bool):    replace one or all values
        '''

        for match in self.find(selection, search):
            value = self._replace(match.row, match.column, search, replace)
            yield match._replace(value=value)

    @exception.except_error(IndexError)
    def paste(self, paste, start):
        '''
        Fill model with `paste` data, starting from index `start`.
        Yields a generator, allowing the view to update it's display.

        Args:
            paste (OrderedDict):    ordered {column: [rows]} with paste data
            start (object):         namedobject with row/column attributes
        '''

        for column_index, series in paste.items():
            column = column_index + start.column

            for row_index, value in enumerate(series):
                row = row_index + start.row
                self.list[column][row] = value

                yield Match(row, column, value, 1)
