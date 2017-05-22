'''
    Objects/Protein/Database/proteins
    _________________________________

    QSqlTableModel for protein databases

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import itertools as it

from collections import namedtuple

from xldlib import chemical

from . import base

# HELPERS
# -------


def molecular_weight(item):
    '''Quick MolecularWeight lookup, returns 0 on an error'''

    try:
        return chemical.Molecule(peptide=item, strict=False).mass
    except KeyError:
        return 0.


# OBJECTS
# -------

Dependent = namedtuple("Dependent", "column function")

# DATA
# ----

DEPENDENTS = {
    'proteins': {
        4: [
            Dependent(5, len),
            Dependent(6, molecular_weight),
        ]
    }
}

# VIEWDATA
# --------

HIDDEN = {
    'proteins': (0, 5, 6),
    'blacklist': (0,),
    'greylist': (0,),
    'named': (0,),
    'decoys': (0,),
    'depricated': (0,)
}
PROTEIN_FIELDS = list(HIDDEN)


# MODEL
# -----


class ProteinModel(base.BaseSqlModel):
    '''Definitions for a QSqlTableModel for protein databases'''

    hidden = HIDDEN

    def __init__(self, *args, **kwds):
        super(ProteinModel, self).__init__(*args, **kwds)

        self.set_bindings()
        self.set_dependents()

    #    SETTERS

    def set_bindings(self):
        '''Connects the dataChanged signal to a a row-wise incrementor'''

        self.dataChanged.connect(self.edited)

    def set_dependents(self, key=None):
        self.dependents = DEPENDENTS.get(key, {})

    #     SLOTS

    def edited(self, topleft, bottomright):
        '''Signal upon a QTabWidgetItem being edited --  add row'''

        self.check_last_row(bottomright)
        self.update_hidden_values(topleft, bottomright)

    def check_last_row(self, index):
        '''Checks if an edited item is truthy and is the last row'''

        text = self.itemFromIndex(index).text()
        if (index.row() == self.row_count - 1) and text:
            self.append_row()

    def update_hidden_values(self, topleft, bottomright):
        '''Sets hidden values that are dependent on other columns'''

        columnrange = range(topleft.column(), bottomright.column() + 1)
        rowrange = range(topleft.row(), bottomright.row() + 1)
        for row, column in it.product(rowrange, columnrange):
            text = self.item(row, column).text()
            for item in self.dependents.get(column, []):
                self.item(row, item.column).setText(item.function(text))

    #    PUBLIC

    def submit_all(self, view=True):
        '''Method which first removes all null rows prior to submitting'''

        if view:
            # check for partial data that can be removed
            columnrange = range(1, self.columnCount())
            for row in reversed(range(self.row_count)):
                data = self.record(row)
                if all(not data.value(i) for i in columnrange):
                    self.removeRow(row)

        if self.submitAll():
            self.database().commit()
        else:
            # unable to commit, rollback to previous
            self.database().rollback()

    def delete(self, *indexes, **kwds):
        '''Sets blank values from a list of QModelIndex entries'''

        # TOOD: use a mixin
        default = kwds.get('default', '')
        if len(indexes) == 1 and isinstance(indexes[0], (list, tuple)):
            indexes = indexes[0]

        for index in indexes:
            self.item(index.row, index.column).setText(default)

#    def get_value(self, row, column):
#        return self.item(row, column).text()

    def get_field(self, table, index, field):
        '''Returns the value from a field from a given table and at an index'''

        self.setTable(table)
        self.select()
        return self.record(index).value(field)

    def paste(self, start, paste):
        '''Executes a paste into the ProteinsTable model'''

        # TOOD: use a mixin
        try:
            for index, series in paste.items():
                column = index + start.column
                for idx, value in enumerate(series):
                    row = start.row + idx
                    self.item(row, column).setText(value)

        except IndexError:
            # too many columns, previous warning
            pass

    def addprotein(self, protein_obj):
        '''Adds a single protein object to the interface'''

        self.fetchall()

        record = self.record()
        record.setValue("Name", protein_obj.name)
        record.setValue("UniProtID", protein_obj.id)

        if record.count() == 7:
            record.setValue("Mnemonic", protein_obj.mnemonic)
            record.setValue("Sequence", protein_obj.sequence)
            record.setValue("Length", protein_obj.length)
            record.setValue("MolecularWeight", protein_obj.mw)

        self.insertRecord(self.rowCount() - 1, record)

    def adddepricated(self, uniprotid):
        '''Adds a depricated protein identifier to the holder'''

        self.fetchall()

        record = self.record()
        record.setValue("Name", 'Depricated')
        record.setValue("UniProtID", uniprotid)

        self.insertRecord(self.rowCount() - 1, record)
