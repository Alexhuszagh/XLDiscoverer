'''
    Gui/Views/Widgets/table
    _______________________

    Display widgets for various utilities QTableWidgets

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import itertools as it
import operator as op

from collections import namedtuple

import six

from PySide import QtCore, QtGui

from xldlib.definitions import partial
from xldlib.qt.objects import views
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.resources import searching
from xldlib.resources.parameters import defaults
from xldlib.utils import logger

from .header import HeaderView
from .helpers import CheckTable, TableItemHelper


# OBJECTS
# -------


class Selection(namedtuple("Selection", "rows columns")):
    '''Subclass with custom initialization'''

    @classmethod
    def fromint(cls, startrow, endrow, startcolumn, endcolumn):
        return cls(Axis(startrow, endrow), Axis(startcolumn, endcolumn))

    @classmethod
    def fromiter(cls, rowiter, columniter):
        rows = Axis(min(rowiter), max(rowiter)+1)
        columns = Axis(min(columniter), max(columniter)+1)
        return cls(rows, columns)

    def iter_cells(self):
        '''# TODO: document, cell-wise iterator'''

        rows = range(self.rows.min, self.rows.max)
        columns = range(self.columns.min, self.columns.max)
        return it.product(rows, columns)

    #    HELPERS

    def tozero(self):
        return Selection(*(i.tozero() for i in self))


class Axis(namedtuple("Axis", "min max")):
    '''Subclass for simplified addition modes'''

    def __add__(self, other):
        '''Either adds to all fields or adds to the current value'''

        if isinstance(other, Axis):
            return Axis(self.min + other.min, self.max + other.max)
        elif isinstance(other, six.integer_types):
            return Axis(self.min + other, self.max + other)
        else:
            return super(Axis, self).__add__(other)

    #    HELPERS

    def tozero(self):
        return Axis(0, self.max - self.min)


class Index(namedtuple("Index", "row column")):
    '''Subclass for simplified addition modes'''

    def __add__(self, other):
        '''Either adds to all fields or adds to the current value'''

        if isinstance(other, Index):
            return Index(self.min + other.min, self.max + other.max)
        elif isinstance(other, six.integer_types):
            return Index(self.min + other, self.max + other)
        else:
            return super(Index, self).__add__(other)


# QTABLES
# -------


class BaseTable(views.BaseView):
    '''
    Defined shared methods through a common object for inheritance
    Methods defined here must be stable between QTableWidgets and QTableViews
    '''

    # QT
    # --
    rows_changed = QtCore.Signal(int)

    # OBJECTS
    # -------
    selection = Selection
    axis = Axis

    #    SETTERS

    def set_widget_styles(self):
        '''Sets the base styles for the QTableWidget'''

        horizontal_header = HeaderView('Horizontal', self)
        self.setHorizontalHeader(horizontal_header)
        horizontal_header.set_resize_mode('Stretch')

        vertical_header = HeaderView('Vertical', self)
        self.setVerticalHeader(vertical_header)
        vertical_header.hide()
        vertical_header.set_resize_mode('Fixed')
        vertical_header.setDefaultSectionSize(qt_config.TABLES['row_height'])

    #    GETTERS

    def get_selected_indexes(self):
        '''
        Returns (row, col) pairs for all cells selected, grouped by row,
        then column.
        :
            get_selected_indexes()->[(0, 1), (0, 2), (0, 3)]
        '''

        selection = self.selectionModel().selection().indexes()
        selection = [(i.row(), i.column()) for i in selection]
        selection.sort(key=op.itemgetter(0))
        if not selection:
            return [Index(0, 1)]

        generator = it.groupby(selection, op.itemgetter(0))
        selection = [Index(*i) for v in generator for i in v[1]]
        return selection


# QTABLEVIEWS
# -----------


class BaseTableView(QtGui.QTableView, BaseTable):
    '''
    This is a base QTableView class for implementing tools to
    facilitate basic tasks, such as item fetching, etc.
    '''

    #    PUBLIC

    #     ITEMS

    def item(self, row, column):
        return self.model().item(row, column)

    def itemFromIndex(self, index):
        return self.model().itemFromIndex(index)

    #     ROWS

    def rowCount(self):
        return self.model().rowCount()

    def columnCount(self):
        return self.model().columnCount()

    def setRowCount(self, rows):
        current = self.rowCount()
        self.model().insertRows(current, rows - current)

    def set_comboboxes(self, row):
        pass


# QTABLEWIDGETS
# -------------


@logger.init('gui', 'DEBUG')
class BaseTableWidget(QtGui.QTableWidget, BaseTable):
    '''
    This is a base QTableWidget class for implementing tools to
    facilitate basic tasks, such as widget styling, getting headers, etc.
    '''

    def __init__(self, parent=None, *qcomboboxes, **kwds):
        super(BaseTableWidget, self).__init__(parent)

        self._datachecker = CheckTable(self, *qcomboboxes)
        self._itemhelper = TableItemHelper(self, *qcomboboxes, **kwds)

        self.set_widget_styles()

    #    SETTERS

    def set_table_properties(self):
        '''
        Assigns the data within the JSON-based dict to a
        QTableWidget, and automatically processes QComboBox
        cellWidgets.
        '''

        # columns and styles
        columns = len(self.model().visible)
        self.setColumnCount(columns)
        self.setHorizontalHeaderLabels(list(self.model().visible.values()))

        # rows and styles
        rows = self.model().row_count + 1
        self.setRowCount(rows)
        for row in range(rows):
            self.set_comboboxes(row)

        # add data
        self.set_data()

    def set_data(self):
        '''Sets data from a FrozenTable to the QTableWidget'''

        for column, attrname in enumerate(self.model().visible):
            column_values = getattr(self.model(), attrname)

            # now iterate over all the rows in column
            for row, value in enumerate(column_values):
                self.set_item(row, column, value)

    def set_item(self, row, column, item):
        '''Adds an item to the QTableWidget'''

        item = self._itemhelper._itemchecker(column, item)
        if isinstance(item, QtGui.QTableWidgetItem):
            self.setItem(row, column, item)

        else:
            self.setCellWidget(row, column, item)

    def set_comboboxes(self, row):
        '''
        Sets cell widgets to QComboBox for all columns defined in
        self.qbomboboxes in that row.
        '''

        horizontal_headers = self.get_horizontal_headers(cast=dict)
        for qcombobox_data in self._itemhelper.qcomboboxes:
            column = horizontal_headers[qcombobox_data.header]
            del column

    def set_selection(self, index):
        fun = partial(self.setCurrentCell, index.row, index.column)
        self.block_once(fun)

    #    GETTERS

    def get_horizontal_headers(self, cast=list):
        '''
        Grabs labels for the horizontal headers, which are used
        as keys for dictionaries in Xl Discoverer modules
        :
            get_horizontal_headers()->['MS Scans', 'Matched Output']
        '''

        horizontal_headers = []
        for column in range(self.columnCount()):
            horizontal_headers.append(self.horizontalHeaderItem(column).text())

        if cast is list:
            return horizontal_headers
        elif cast is tuple:
            return tuple(horizontal_headers)
        elif cast is dict:
            return {k: v for k, v in enumerate(horizontal_headers)}

    def get_column(self, column):
        '''Returns the values from a given column'''

        for row in range(self.rowCount()):
            item = self.item(row, column)
            if item is not None:
                yield item.text()

    #    HELPERS

    def update_rows(self, last_row):
        '''Styles rows upon row number change.'''

        rows = self.rowCount()
        for row in range(last_row, rows):
            self.set_comboboxes(row)

    def check_last_row(self, row):
        '''Updates the widget dimensions upon setting values'''

        rows = self.rowCount()
        if row == rows - 1:
            self.setRowCount(rows + 1)
            self.set_comboboxes(rows)
            self.rows_changed.emit(rows)

    def check_data(self):
        self._datachecker.check_data()

    def selectionrange(self, inselection=None):
        '''Returns the current selection range for the widget'''

        if inselection is None:
            inselection = defaults.DEFAULTS['search_in_selection']

        selection = self.get_selected_indexes()
        if inselection and len(selection) > 1:
            # in selection and more than 1 item selected
            return Selection.fromiter(*zip(*selection))
        else:
            rows = min(self.rowCount(), self.model().row_count)
            columns = min(self.columnCount(), self.model().column_count)
            return Selection.fromint(0, rows, 0, columns)

    @logger.call('gui', 'debug')
    @logger.except_error(StopIteration)
    def find(self):
        '''Finds the first item matching the given query'''

        search = searching.get_search()
        selection = self.selectionrange()
        index = next(self.model().find(selection, search))
        self.set_selection(index)

    @logger.call('gui', 'debug')
    def findall(self):
        '''Finds all items matching the given query'''

        search = searching.get_search()
        selection = self.selectionrange()
        return list(self.model().find(selection, search))

    @logger.call('gui', 'debug')
    @logger.except_error(IndexError)
    def replace(self):
        '''Replaces the first match in the table and updates the model'''

        search, replace = searching.get_replace()
        selection = self.selectionrange()
        index = next(self.model().replace(selection, search, replace))
        self.set_item(index.row, index.column, index.value)
        self.set_selection(index)

    @logger.call('gui', 'debug')
    def replaceall(self):
        '''Replaces all matches within the table'''

        search, replace = searching.get_replace()
        selection = self.selectionrange()
        counts = []
        for index in self.model().replace(selection, search, replace, True):
            self.set_item(index.row, index.column, index.value)
            counts.append(index.number)

        # update the current selection to the last item
        if counts:
            self.set_selection(index)

        return counts

    @logger.call('gui', 'debug')
    def paste(self, paste, start):
        '''Pastes data into the QTableWidget'''

        for index in self.model().paste(paste, start):
            self.set_item(index.row, index.column, index.value)

# EDITING
# -------


@logger.init('gui', 'DEBUG')
class TableNoEdit(BaseTableWidget):
    '''
    Non-editable implementation of QTable. Implemented for ColumnDialogs,
    find/replace reports, etc.
    '''

    def __init__(self, *args, **kwds):
        super(TableNoEdit, self).__init__(*args, **kwds)

        self.setEditTriggers(qt.EDIT_TRIGGER['No'])
        self.setSelectionBehavior(qt.SELECTION_BEHAVIOR['Items'])
        self.setSelectionMode(qt.SELECTION_MODE['Single'])
