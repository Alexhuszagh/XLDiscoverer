'''
    Controllers/Bindings/table
    __________________________

    Class with designed inheritance for copy/paste methods.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtCore

from xldlib.definitions import partial
from xldlib.onstart.main import APP
from xldlib.qt.objects import base, threads
from xldlib.qt import resources as qt

from . import copier, decorators, paster


# MUTEX
# -----

MUTEX = threads.ContextMutex(QtCore.QMutex.Recursive)


# SLOTS
# -----


def nullslot(result):
    pass


def copyslot(result):
    APP.clipboard().setText(result)


# OBJECTS
# -------


class TableBindings(base.BaseObject):
    '''Provides methods to bind to QKeyShortcuts for facilitated table use'''

    def __init__(self, table):
        super(TableBindings, self).__init__(table)

        self.table = table
        self.copier = copier.HandleCopy(self.table)
        self.paster = paster.HandlePaste(self.table)

        self.set_shortcuts()

    # PUBLIC FUNCTIONS

    @decorators.newspinner(nullslot)
    def delete(self):
        self._delete()

    def _delete(self, blank=""):
        '''
        Excel-like delete function. Deletes contents in all selected cells.
            delete() -> void
            (Row, Column) [Value] Selection: -->
            (1,2) ["AA"], (1,3) ["BB"], (2,2) ["CC"], (2,3) ["DD"]
            --> (1,2) [], (1,3) [], (2,2) [], (2,3) []
        '''

        selected_indexes = self.table.get_selected_indexes()
        items = (self.table.item(i.row, i.column) for i in selected_indexes)
        filtered = [i for i in items if i is not None]

        for item in filtered:
            item.setText(blank)

        self.table.model().delete(selected_indexes)

        if filtered and hasattr(self.table, "changed"):
            self.table.changed = True

    @decorators.newspinner(copyslot)
    def cut(self):
        '''Combines copy and delete operations for cut functionality'''

        result = self.copier.copy()
        self._delete()
        return result

    @decorators.newspinner(copyslot)
    def copy(self):
        return self.copier.copy()

    def paste(self):
        clipboard_text = self.app.clipboard().text()
        self._paste(clipboard_text)

    @decorators.newspinner(nullslot)
    def _paste(self, clipboard_text):
        self.paster.paste(clipboard_text)

    def select_all(self):
        '''Selects all item in the table'''

        with MUTEX:
            model = self.table.selectionModel()
            mode = self.table.selectionMode()
            self.table.setSelectionMode(qt.SELECTION_MODE['Extended'])

            # clear selection
            model.clearSelection()
            selection = model.selection()

            # reset the selection mode for all items
            for column in range(self.table.columnCount()):
                # only select visible items
                if not self.table.isColumnHidden(column):
                    self.table.selectColumn(column)
                    selection.merge(model.selection(), qt.SELECTION_MODEL['Select'])
            self.table.setSelectionMode(mode)

    def select_mode(self, mode=None):
        '''
        Changes the QTableSelectionMode between the list options.
            mode -- QtGui.QAbstractItemView.<atribute>
               ExtendedSelection
               SingleSelection
               MultiSelection
            select_mode(QtGui.QAbstractItemView.ExtendedSelection)
        '''

        mode = mode or qt.SELECTION_MODE['Extended']
        self.table.setSelectionMode(mode)
        self.table.blockSignals(mode != qt.SELECTION_MODE['Single'])

    #     GETTERS

    def set_shortcuts(self):
        self.shortcuts = {
            'Ctrl+f': self.table.finder.show,
            'Ctrl+b': self.table.block,
            'Ctrl+c': self.copy,
            'Ctrl+x': self.cut,
            'Ctrl+v': self.paste,
            'Del': self.delete,
            'Ctrl+a': self.select_all
        }

        modes = {
            'Ctrl+Shift+s': 'Single',
            'Ctrl+Shift+m': 'Multi',
            'Ctrl+Shift+e': 'Extended'
        }
        for keysequence, mode in modes.items():
            fun = partial(self.select_mode, qt.SELECTION_MODE[mode])
            self.shortcuts[keysequence] = fun
