'''
    Gui/Controllers/Objects/checktable
    __________________________________

    Helper functions for a QTableWidget data consistency and integrity.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.controllers import messages
from xldlib import exception
from xldlib.utils import math_

# load objects/functions
from xldlib.definitions import partial


# DATA
# ----

NULL = {None, "", 0, 0.}


# FUNCTIONS
# ---------


def isnull(item):
    '''Evaluates to true if the object is NaN, inf, a null string or None'''

    return item in NULL or math_.isnan(item)


# OBJECTS
# -------


class CheckTable(messages.BaseMessage):
    '''Definition for QTableWidget data checkers'''

    def __init__(self, table, *qcomboboxes):
        super(CheckTable, self).__init__()

        self.table = table
        self.set_static()

    #    SETTERS

    def set_static(self):
        '''Binds static methods to the class'''

        self.isnull = isnull

    def reset_item(self, index, row, column):
        '''Remakes a given item to avoid reparenting the given object'''

        item = self.table.takeItem(index + 1, column)

        # block insertion to avoid table signals
        fun = partial(self.table.set_item, index, column, item)
        self.block_once(fun)

    #    DELETERS

    def delete_row(self, row, rows):
        '''Deletes the row from the widget and then adjusts the table'''

        for column in reversed(range(self.table.columnCount())):
            column_values = self.model().list[column]
            if row < len(column_values):
                del column_values[row]

        rows = self.table.rowCount() - 1
        adjust_rowcount = partial(self.table.setRowCount, rows)
        self.table.block_once(adjust_rowcount)

    #    HELPERS

    def model(self):
        return self.table.model()

    def check_data(self):
        '''Checks the input data, and finally adjusts the row count'''

        self.verify_data()
        return self.adjust_rows()

    @messages.warningbox(AssertionError)
    def verify_data(self):
        '''Ensures data integrity prior to widget closing or saving'''

        self.check_column_length()
        self.check_null_data()
        self.table.verify_fields()

    def check_column_length(self):
        '''Checks that all columns have equal-length values within the data'''

        lengths = []
        for attrname in self.model().visible:
            column_values = getattr(self.model(), attrname)
            length = len([i for i in column_values if not self.isnull(i)])
            lengths.append(length)

        assert all(i == length for i in lengths), exception.CODES['004']

    def check_null_data(self):
        '''Checks that no null data exists within the object'''

        keys = list(self.model().visible.values())
        for row in range(self.model().length):
            null = [self.isnull(self.model()[k].get(row)) for k in keys]
            assert all(null) or not any(null), exception.CODES['004']

    def adjust_rows(self):
        '''Adjusts the number of rows in the QTableWidget off the data'''

        changed = False
        rows = self.model().row_count
        for row in reversed(range(rows)):
            if not self.check_row(row):
                self.delete_row(row, rows)
                changed = True

        return changed

    def check_row(self, row):
        '''Checks to see if any rows with no data entered.'''

        lst = []
        for column in range(self.table.columnCount()):
            value = self.model().list[column].get(row)
            lst.append(value)

        return any(i for i in lst if not self.isnull(i))
