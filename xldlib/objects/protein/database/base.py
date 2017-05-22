'''
    Objects/Protein/database/table
    ______________________________

    Base model definition for the QSqlTableModel.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtCore, QtSql

from . import table


# MODELS
# ------


class BaseSqlModel(QtSql.QSqlTableModel):
    '''Definitions for simplified QtSql parameters'''

    # ROWS
    # ----
    _appended = False

    def __init__(self, *args, **kwds):
        super(BaseSqlModel, self).__init__(*args, **kwds)

    #   PROPERTIES

    #   PROPERTIES

    @property
    def length(self):
        '''Returns the total number of rows within the model'''

        query = self.query()
        sqlquery = "SELECT Count(*) FROM {}".format(self.tableName())
        if query.exec_(sqlquery) and query.next():
            return query.record().value(0)
        return -1

    @property
    def rows(self):
        return range(self.length)

    @property
    def columns(self):
        import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        raise NotImplementedError

    @property
    def row_count(self):
        return self.length

    @property
    def column_count(self):
        import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        return len(self.columns)

    @property
    def list(self):
        import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()
        return self._list

    @property
    def appended(self):
        return self._appended

    @appended.setter
    def appended(self, value):
        self._appended = value

    #     PUBLIC

    def fetchMore(self, index=None):
        '''Custom implementation which appends a row on the first instance'''

        if index is None:
            # set an invalid index, which still works for the base class
            index = QtCore.QModelIndex()

        # call the default base class
        super(BaseSqlModel, self).fetchMore(index)

        if not self.appended and not self.canFetchMore(index):
            # add a new row at the end when no more can be fetched
            self.append_row()
            self.appended = True

    def fetchall(self):
        '''Fetch all items within the model'''

        while self.canFetchMore():
            self.fetchMore()

    #     ITEMS

    def item(self, row, column):
        return table.QTableModelItem(self.index(row, column))

    def itemFromIndex(self, index):
        return table.QTableModelItem(index)

    #    TABLES

    def change_table(self, key):
        '''Changes the currently open table and sets dependent columns'''

        self.appended = False
        self.setTable(key)
        self.select()

        self.set_dependents(key)

    def append_row(self):
        return self.insertRow(self.row_count)
