'''
    Controllers/Bindings/copier
    ___________________________

    Inheritable methods to perform copy operations in table-like Qt
    objects.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os

from xldlib.general import mapping
from xldlib.qt.objects import base


# OBJECTS
# -------


class HandleCopy(base.BaseObject):
    r'''
    OpenOffice-like copy function. Modular component of a QTableWidget or
    QTableView to provide copy functionality. Clips current selection
    to the clipboard, using a column-wise delimiter ('\t') and a row-wise
    delimiter (os.linesep).
    '''

    # DELIMITERS
    # ----------
    row_delimiter = os.linesep
    column_delimiter = '\t'

    def __init__(self, table):
        super(HandleCopy, self).__init__(table)

        self.table = table

    #     PUBLIC

    def copy(self):
        '''Clip current table selection to clipboard'''

        selected_indexes = self.table.get_selected_indexes()
        values = self._get_values(selected_indexes)

        # join into a string and set to the clipboard
        rows = (self.column_delimiter.join(i) for i in values.values())
        return self.row_delimiter.join(rows)

    #   NON-PUBLIC

    def _get_values(self, selected_indexes):
        '''
        Grab QTable cell values from the corresponding indexes

        Args:
            selected_indexes (list): objects with row/column variables
        Returns (dict): dict with {row: [values]}
        '''

        values = mapping.OrderedDefaultdict(list)
        for index in selected_indexes:
            value = self.table.model().list[index.column][index.row]
            #value = self.table.model().get_value(index.row, index.column)
            if value is not None:
                values[index.row].append(value)

        return values
