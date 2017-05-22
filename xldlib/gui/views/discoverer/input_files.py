'''
    Gui/Views/Crosslink_Discoverer/input_files
    __________________________________________

    Input files widget for CrossLink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os

from PySide import QtCore, QtGui

from xldlib import exception
from xldlib.definitions import partial
from xldlib.controllers import bindings
from xldlib.gui.views.dialogs import contextbar
from xldlib.qt import resources as qt
from xldlib.resources import extensions
from xldlib.resources.parameters import input_files
from xldlib.utils import decorators, logger
from xldlib.utils.io_ import qtio

from .. import widgets
from ..dialogs import findreplace


# DATA
# ----

WIDGETS = [
    ('Level Separated', 'level_separated'),
    ('Hierarchical', 'hierarchical')
]


# CONTEXTS
# --------


class InputFilesContext(contextbar.ContextBar):
    _windowkey = 'table'


# QTABLEWIDGET
# ------------


@logger.init('gui', 'DEBUG')
class InputFilesTable(widgets.TableNoEdit, bindings.Keys):
    '''QTable for Inputting Files to Xl Discoverer'''

    def __init__(self, parent, model):
        super(InputFilesTable, self).__init__(parent, basename=True)

        self._model = model
        self.finder = findreplace.FindReplace(self)

        self.set_table_properties()
        self.set_table_data()

        self.setAcceptDrops(True)

    #  EVENT HANDLING

    def keyPressEvent(self, event):
        '''Overrides an enter event to connect to a set_file'''

        if event.key() in {qt.KEY['Enter'], qt.KEY['Return']}:
            self.set_file(self.currentRow(), self.currentColumn())

        else:
            super(InputFilesTable, self).keyPressEvent(event)

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        '''Adds the data from the filepath if it exists on a drop'''

        data = event.mimeData()
        row = self.rowAt(event.pos().y())
        column = self.columnAt(event.pos().x())

        if data.hasUrls():
            urls = data.urls()
            # skip multiple files, since single cell
            if len(urls) == 1:

                # skip directories, etc.
                path = urls[0].toLocalFile()
                if os.path.isfile(path):
                    self.set_file(row, column, path=path)

    #     SETTERS

    def set_table_data(self):
        '''Initializes the table and sets the table data'''

        self.set_size_policy('Expanding', 'Expanding')

        self.bind_table()
        self.bind_save(self.parent().save)
        self.currentCellChanged.connect(self.set_file)
        self.cellDoubleClicked.connect(self.set_file)
        self.rows_changed.connect(self.update_rows)

    @decorators.overloaded
    def set_file(self, row, column, **kwds):
        '''Sets a new file to a cell widget'''

        path = kwds.get('path')
        if path is None:
            path = self.get_file_path(row, column)

        # store the retrieved data
        column_values = self.model().list[column]
        column_values[row] = path
        self.set_item(row, column, path)

        if path:
            self.check_last_row(row)

    #     GETTERS

    def get_file_path(self, row, column):
        path = self.get_directory(row, column)
        return qtio.getopenfile(self, path=path, suffix=extensions.RAW)

    def get_directory(self, row, column):
        '''Returns the row/directory for the QFileDialog'''

        column_values = self.model().list[column]
        if row < len(column_values) and column_values[row]:
            return str(column_values[row])

    #     HELPERS

    def model(self):
        return self._model

    def process_fields(self):
        '''Shell function in case I need to process the data later'''

    def verify_fields(self):
        '''Ensures all the data is properly assigned within the widget'''

        for attrname in self.model().visible:
            column_values = getattr(self.model(), attrname)
            generator = (os.path.exists(i) for i in column_values if i)
            assert all(generator), exception.CODES['026']


# RETURN/SAVE
# -----------


@logger.init('gui', 'DEBUG')
class ButtonSection(widgets.Widget):
    '''Provides a button section to control the visible table'''

    def __init__(self, input_files, parent):
        super(ButtonSection, self).__init__(parent)

        self.input_files = input_files

        self.set_layout(QtGui.QVBoxLayout)
        self.set_widgets()
        self.toggle_checkstate()

    #     SETTERS

    def set_widgets(self):
        '''Sets the target widgets for the layout'''

        self.set_savebar()
        self.layout.addWidget(widgets.SunkenDivider(self))

        self.set_hierarchical()
        self.set_clearall()
        self.layout.addWidget(widgets.Divider(self))

    def set_savebar(self):
        '''Adds a return/save bar to the layout'''

        layout = QtGui.QHBoxLayout()
        self.layout.addLayout(layout)

        done_editing = widgets.ClickButton("Done Editing", self.parent().close)
        layout.addWidget(done_editing)

        save = widgets.ClickButton("Save", self.parent().save)
        layout.addWidget(save)

    def set_hierarchical(self):
        '''Makes the hierarchical/level separated toggle buttons'''

        layout = QtGui.QHBoxLayout()
        self.layout.addLayout(layout)

        for title, attrname in WIDGETS:
            slot = partial(self.clicked, attrname)
            button = widgets.ClickButton(title, slot, checkable=True)
            layout.addWidget(button)
            setattr(self, attrname, button)

    def set_clearall(self):
        '''Adds a widget which clears the parent table'''

        clear_all = widgets.ClickButton("Clear All", self.parent().clear)
        self.layout.addWidget(clear_all)

    #     HELPERS

    def clicked(self, key):
        '''
        Changes the current hierarchical/level_separated checksattes
        and the input_files backing store.
        '''

        self.input_files.current = key
        self.toggle_checkstate()

        self.parent().change_table()

    def toggle_checkstate(self):
        '''
        Toggles the current checkstates for the level_separated/hierarchical
        input mods
        '''

        level_separated = self.input_files.level_separated
        self.level_separated.setChecked(level_separated)
        self.hierarchical.setChecked(not level_separated)


# INPUT VIEW
# ----------


@logger.init('gui', 'DEBUG')
class InputFilesView(QtGui.QWidget, bindings.Keys):
    '''
    QTableWidget with QFileDialog-bound items.
    Displays basename for each item, while simultaneously storing
    a fullpath copy. Enables search/replace features on full-path
    items.
    Aims:
        -- Easy file addition with visual pairing of MS data and
            paired peptides
        -- Simplified display of the MS data for quick debugging.
    '''

    closed = QtCore.Signal(object)

    def __init__(self, parent, quantitative):
        super(InputFilesView, self).__init__(parent)

        self.input_files = input_files.INPUT_FILES.get_table(quantitative)

        self.set_layout(QtGui.QVBoxLayout)
        self.set_widgets()
        self.set_context()

        self.show()

    #     SETTERS

    def set_widgets(self):
        '''Sets the target widgets for the layout'''

        buttons = ButtonSection(self.input_files, self)
        self.layout.addWidget(buttons)

        self.table = InputFilesTable(self, self.input_files.current_table)
        self.layout.addWidget(self.table)

    def set_context(self):
        '''Adds a context bar to the current window'''

        self.context = InputFilesContext(self, qt.INPUT_TABLE_BAR)
        self.bind_keys({'Ctrl+?': self.context.show})

    #     HELPERS

    def save(self):
        '''Saves the data in the currently visible table'''

        changed = self.table.check_data()
        input_files.INPUT_FILES.save()

        if changed:
            self.table.clearContents()
            self.table.set_table_properties()

    def clear(self):
        '''Clears the data from the visible table'''

        self.table.block_once(self.table.clearContents)
        for column_values in self.table.model().values():
            del column_values[:]
        self.table.block_once(partial(self.table.setRowCount, 1))

    def change_table(self):
        '''Changes the table after changing the input mod switch'''

        self.table.hide()
        self.layout.removeWidget(self.table)
        self.table.deleteLater()

        self.table = InputFilesTable(self, self.input_files.current_table)
        self.layout.addWidget(self.table)

    #  EVENT HANDLING

    def closeEvent(self, event):
        '''Shows the parent menu widget upon a close event'''

        self.table.check_data()

        self.closed.emit(self)
        event.accept()
