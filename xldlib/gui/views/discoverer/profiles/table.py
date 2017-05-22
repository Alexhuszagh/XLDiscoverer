'''
    Gui/Views/Crosslink_Discoverer/Profiles/table
    _____________________________________________

    Editable table with QEventFilters bound for each embedded QComboBox.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtCore, QtGui

from xldlib.gui.views import widgets
from xldlib.qt.objects import base
from xldlib.qt import resources as qt
from xldlib.resources import chemical_defs
from xldlib.utils import decorators, logger


# CELL
# ----


@logger.init('gui', 'DEBUG')
class ModificationCell(widgets.ListViewBox):
    '''A QComboWidget for a single cell'''

    def __init__(self, parent, column, row):
        super(ModificationCell, self).__init__(parent)

        self.column = column
        self.row = row

        self.set_modification()

        self.addItem(self.name)
        self.activated.connect(self.update_modification)

    #   PROPERTIES

    @property
    def table(self):
        return self.parent().parent()

    @property
    def profile(self):
        return self.table.parent().profile

    @property
    def used(self):
        return {i.id for i in self.column.widgets if self.is_used(i)}

    @property
    def unused(self):
        return self.column.lookup - self.used

    #    PUBLIC

    @decorators.overloaded
    def update_modification(self):
        '''Updates the current population with the new modification'''

        # get the current id
        text = self.currentText()
        id_ = self.column.names.get(text, None)

        if self.row < len(self.column):
            self.column[self.row] = id_
        elif text:
            while len(self.column) < self.row:
                self.column.append(None)
            self.column.append(id_)

        if self.is_empty_row():
            self.delete_row()
        elif text and self.is_last_row():
            self.append_row()

    #    SETTERS

    def set_modification(self):
        '''Sets the current modification and name'''

        if self.row >= len(self.column):
            self.id = None
        else:
            self.id = self.column[self.row]

        if self.id is not None:
            self.name = chemical_defs.MODIFICATIONS[self.id].tostr()
        else:
            self.name = ''

    #    HELPERS

    def is_used(self, item):
        return (item != self) and (item.id is not None)

    def is_empty_row(self):
        '''Deletes all elements in the current row and repaints the widget'''

        modifications = (i.modifications for i in self.profile.populations)
        filtered = (i for i in modifications if self.row < len(i))
        return all(i[self.row] is None for i in filtered)

    def delete_row(self):
        '''Deletes all elements in the current row and repaints the widget'''

        for population in self.profile.populations:
            if self.row < len(population.modifications):
                del population.modifications[self.row]
        self.reset_view()

    def is_last_row(self):
        return self.row == self.table.rowCount() - 1

    def append_row(self):
        '''Adds a row to the current table'''

        rows = self.table.rowCount()
        self.table.setRowCount(rows + 1)

        for column in self.table.columns:
            column.set_widget(rows)

    def reset(self):
        '''Resets the QCombobox items from a memo'''

        names = sorted(self.column.ids[i] for i in self.unused)
        names.append('')

        self.clear()
        for name in names:
            self.addItem(name)

        index = names.index(self.name)
        self.setCurrentIndex(index)

    def reset_view(self):
        self.table.reset_view()


# LOOKUP
# ------


class Modifications(dict):
    '''Modifications dict with lookup for IDs and names'''

    def __init__(self, *modifications):
        super(Modifications, self).__init__()

        self._ids = {}
        self._names = {}
        self._lookup = set()

        for modification in modifications:
            self[modification.id] = modification

    #   PROPERTIES

    @property
    def ids(self):
        return self._ids

    @property
    def names(self):
        return self._names

    @property
    def lookup(self):
        return self._lookup

    #     MAGIC

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        '''M[k] = v -> M({k: v})'''

        string = value.tostr()
        self.ids[key] = string
        self.names[string] = key
        self.lookup.add(key)

        dict_setitem(self, key, value)

    def __delitem__(self, key, dict_delitem=dict.__delitem__):
        '''del M[k] -> M()'''

        string = self.ids.pop(key)
        del self.names[string]
        self.lookup.remove(key)

        dict_delitem(self, key)


# COLUMNS
# -------


class Column(base.BaseObject):
    '''Implementation with a memoized set and other attributes'''

    def __init__(self, profile, column, rows, parent):
        super(Column, self).__init__(parent)

        self.column = column
        self.population = profile.populations[column]
        self.rows = rows
        self.set_modifications(profile.engine)
        self.widgets = []

        for row in range(rows):
            self.set_widget(row)

    #      MAGIC

    def __iter__(self):
        return iter(self.widgets)

    def __len__(self):
        return len(self.population.modifications)

    def __getitem__(self, index):
        return self.population.modifications[index]

    def __setitem__(self, index, value):
        self.population.modifications[index] = value

    #   PROPERTIES

    @property
    def ids(self):
        return self.modifications.ids

    @property
    def names(self):
        return self.modifications.names

    @property
    def lookup(self):
        return self.modifications.lookup

    #     PUBLIC

    def append(self, value):
        self.population.modifications.append(value)

    #     SETTERS

    def set_widget(self, row):
        widget = self.parent().new_widget(self, row, self.column)
        self.widgets.append(widget)

    def set_modifications(self, engine):
        '''Sets the current modifications for the column widget'''

        ids = chemical_defs.MODIFICATIONS.get_engine(engine)
        modifications = (chemical_defs.MODIFICATIONS[i] for i in ids)
        standard = (i for i in modifications if not i.fragment)

        self.modifications = Modifications(*standard)

# HEADERS
# -------


class EditableHeader(widgets.HeaderView):
    '''
    Installs a QLineEdit on the viewport() to make an editable
    QHeaderView which is installed on a QTableWidget.
    '''

    header_changed = QtCore.Signal(int, str)

    def __init__(self, orientation, parent=None):
        super(EditableHeader, self).__init__(orientation, parent)

        self.set_options()
        self.set_lineedit()

        self.sectionedit = 0

        # Connects to double click
        self.sectionDoubleClicked.connect(self.editHeader)
        self.lineedit.editingFinished.connect(self.doneEditing)
        # set resizeMode
        self.setResizeMode(QtGui.QHeaderView.Stretch)

    #  EVENT HANDLING

    def doneEditing(self):
        '''Overrides public doneEditing signal to set header text.'''

        # Need to block signals or there are no rows after
        self.lineedit.blockSignals(True)
        self.lineedit.setHidden(True)
        # grab name and reset header
        new_name = str(self.lineedit.text())
        self.header_changed.emit(self.sectionedit, new_name)
        self.parent().setHorizontalHeaderLabels(self.parent().headers)
        self.lineedit.setText('')

    def editHeader(self, section):
        '''This block sets up the geometry for the line edit'''

        edit_geometry = self.lineedit.geometry()
        edit_geometry.setWidth(self.sectionSize(section))
        edit_geometry.moveLeft(self.sectionViewportPosition(section))
        self.lineedit.setGeometry(edit_geometry)
        # grab the text
        text = self.parent().headers[section]
        # set the lineedit
        self.lineedit.setText(text)
        self.lineedit.setHidden(False)
        self.lineedit.blockSignals(False)
        self.lineedit.setFocus()
        self.lineedit.selectAll()
        self.sectionedit = section

    #     SETTERS

    def set_options(self):
        '''Sets the default options for the class'''

        self.setMovable(True)
        self.setClickable(True)

    def set_lineedit(self):
        '''Install a lineEdit on the viewport() to intercept viewport events'''

        # set up the viewport as a LineEdit
        self.lineedit = QtGui.QLineEdit(parent=self.viewport())
        self.lineedit.setAlignment(qt.ALIGNMENT['Top'])
        # need to block signals to override native Qt signals
        self.lineedit.setHidden(True)
        self.lineedit.blockSignals(True)


# TABLE
# -----


@logger.init('gui', 'DEBUG')
class TableView(widgets.BaseTableWidget):
    '''Table view with editable headers to edit the profile names'''

    def __init__(self, parent):
        super(TableView, self).__init__(parent)

        self.set_size_policy('Expanding', 'Expanding')
        self.set_header()
        self.set_view()

    #    PROPERTIES

    @property
    def profile(self):
        return self.parent().profile

    @property
    def headers(self):
        return self.profile.headers

    #  EVENT HANDLING

    def eventFilter(self, widget, event, return_state=False):
        '''Intercepts QComboBox events to force a unique list of values'''

        if not isinstance(widget, QtGui.QComboBox):
            event.accept()

        elif (hasattr(event, "buttons")
            and event.buttons() == qt.MOUSE['Left']):
            widget.block_once(widget.reset)
            event.accept()

        return return_state

    #     SETTERS

    def set_header(self):
        '''Sets the editable header'''

        self.header = EditableHeader('Horizontal', self)
        self.header.header_changed.connect(self.rename)
        self.setHorizontalHeader(self.header)

    def set_view(self):
        '''Sets the initial view'''

        self.set_headerdata(self.profile)
        self.set_data(self.profile)

    def set_headerdata(self, profile):
        '''Sets the QTableWidget's header labels'''

        self.setRowCount(profile.row_count + 1)
        self.setColumnCount(profile.column_count)
        self.setHorizontalHeaderLabels(profile.headers)

    def set_data(self, profile):
        '''Sets the qcombobox cell widgets and adds event filters'''

        rows = profile.row_count + 1
        self.columns = []
        for column, population in enumerate(profile.populations):
            columnwidgets = Column(profile, column, rows, self)
            self.columns.append(columnwidgets)

    def set_cell_widget(self, row, column, item):
        item.installEventFilter(self)
        self.setCellWidget(row, column, item)

    #     HELPERS

    def new_widget(self, columnwidgets, row, column):
        '''Creates, sets, and returns a new cell widget'''

        widget = ModificationCell(self, columnwidgets, row)
        self.set_cell_widget(row, column, widget)

        return widget

    def rename(self, index, name):
        self.profile.rename(index, name)

    def reset_view(self):
        '''Clears the table's contents and header'''

        del self.columns[:]
        self.clear()
        self.set_view()
