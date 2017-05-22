'''
    Gui/Views/Dialogs/FindReplace
    _____________________________

    Binding for executing find/replace queries in QTableWidgets.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtCore, QtGui

from xldlib.controllers import messages
from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger

from .base import KeyBindingDialog


# QTABLEWIDGETS
# -------------


@logger.init('gui', 'DEBUG')
class ReportTable(widgets.BaseTableWidget):
    '''Non-editable variant of a QTableWidget to be embedded in a QDialog'''

    def __init__(self, parent, model, horizontalheaders):
        super(ReportTable, self).__init__(parent)

        self._model = model
        self.horizontalheaders = horizontalheaders

        self.set_table_properties()
        self.set_data()

    #    PROPERTIES

    @property
    def model(self):
        return self._model

    #     SETTERS

    def set_table_properties(self, columns=("Row", "Column", "Value")):
        '''Assign metadata for the QTableWidget'''

        # columns and styles
        self.setRowCount(len(self.model))
        self.setColumnCount(len(columns))
        self.setHorizontalHeaderLabels(columns)

        self.setEditTriggers(qt.EDIT_TRIGGER['No'])

    def set_data(self):
        '''Set data from a list to the QTableWidget'''

        for row, query in enumerate(self.model):
            self.setitem(row, column=0, item=str(query.row))

            column = self.horizontalheaders[query.column]
            self.setitem(row, column=1, item=column)

            self.setitem(row, column=2, item=query.value)

    def setitem(self, row, column, item):
        '''Add an item to the QTableWidget with no edit flags'''

        item = self._itemhelper._itemchecker(column, item)
        item.setFlags(qt.ITEM['No'])
        self.setItem(row, column, item)


# DIALOG
# ------


@logger.init('gui', 'DEBUG')
class ReportFindAll(KeyBindingDialog):
    '''
    QDialog containing a non-editable QTableWidget to report
    the row, horizontal header, and name of all matches from a find
    all search.
    '''

    # QT
    # --
    _qt = qt_config.DIALOGS
    _windowkey = 'findall'

    def __init__(self, parent, *args):
        super(ReportFindAll, self).__init__(parent)

        self.set_layout(QtGui.QVBoxLayout)
        self.set_widgets(*args)
        self.set_window_data()
        self.bind_close()

        self.set_fixed_size_qt()
        self.move_qt()

    #     SETTERS

    def set_widgets(self, *args):
        '''Add the child widgets to the current layout'''

        self.table = ReportTable(self, *args)
        self.layout.addWidget(self.table)

        self.closebutton = widgets.ClickButton("Close", self.close)
        self.layout.addWidget(self.closebutton)

    def set_window_data(self):
        '''Set the current window data for the QDialog'''

        self.set_top_window()
        self.setWindowTitle("Find All Summary")


@logger.init('gui', 'DEBUG')
class FindReplace(KeyBindingDialog, messages.BaseMessage):
    '''
    QDialog widget encapsulating widgets allowing the user to find,
    replace values within a QTableWidget via substring matching and
    configure case matching or searching only in selection.

    -----------------------
    -  ---  -------  ---  -
    -  ---  -------  ---  -
    -                     -
    -  ------  ----- ---  -

    -  ---  -------  ---  -
    -  ---  -------  ---  -
    -----------------------

    '''

    # QT
    # --
    _qt = qt_config.DIALOGS
    _windowkey = 'find'

    def __init__(self, parent):
        super(FindReplace, self).__init__(parent)

        self.moveEvent = self.track_move_event
        self.resizeEvent = self.ignore_resize_event

        self.set_layout(QtGui.QGridLayout)
        self.set_widgets()
        self.set_window_data()

        self.set_fixed_size_qt()
        self.move_qt()

    #    PROPERTIES

    @property
    def table(self):
        return self.parent()

    @property
    def model(self):
        return self.parent().model()

    #  EVENT HANDLING

    def showEvent(self, event):
        '''Override showEvent to undo minimize flags'''

        if self.windowState() & QtCore.Qt.WindowMinimized:
            flags = self.windowState() & ~QtCore.Qt.WindowMinimized
            self.setWindowState(flags)

        super(FindReplace, self).showEvent(event)

    @logger.call('gui', 'debug')
    def closeEvent(self, event):
        event.ignore()
        self.hide()

    @logger.call('gui', 'debug')
    def changeEvent(self, event):
        '''Override changeEvent to hide window on minimize event'''

        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & QtCore.Qt.WindowMinimized:
                event.ignore()
                self.hide()
        else:
            super(FindReplace, self).changeEvent(event)

    #     SETTERS

    def set_widgets(self):
        '''Initialize widgets within layout'''

        self.__set_search()
        self.__set_conditions()
        self.__set_replace()
        self.__set_buttons()

    def set_window_data(self):
        '''Set window data for the QDialog'''

        self.set_top_window()
        self.setWindowTitle("Find/Replace")

    def __set_search(self):
        '''Set search bar and QLineEdit form'''

        label = widgets.Label("Search For:")
        self.layout.addWidget(label, 0, 0, 6, 2)

        storage = updating.Storage('search_form')
        self.searchform = updating.LineEdit(self, storage,
            tooltip="Search query.")
        self.layout.addWidget(self.searchform, 0, 2, 6, 4)

    def __set_conditions(self):
        '''Set updating checkboxes describing search parameters'''

        storage = updating.Storage('search_case_sensitive')
        self.casesensitive = updating.CheckBox("Case Sensitive", self, storage,
            tooltip="Force case matches during search queries")
        self.layout.addWidget(self.casesensitive, 6, 0, 6, 3)

        storage = updating.Storage('search_in_selection')
        self.inselection = updating.CheckBox("In Selection", self, storage,
            tooltip="Search exclusively within the current selection")
        self.layout.addWidget(self.inselection, 6, 3, 6, 3)

    def __set_replace(self):
        '''Set replace bar and QLineEdit form'''

        label = widgets.Label("Replace With:")
        self.layout.addWidget(label, 12, 0, 6, 2)

        storage = updating.Storage('replace_form')
        self.replaceform = updating.LineEdit(self, storage,
            tooltip="Search query.")
        self.layout.addWidget(self.replaceform, 12, 2, 6, 4)

    def __set_buttons(self):
        '''Set vertical buttons in last column'''

        self.findbutton = QtGui.QPushButton("Find")
        self.findbutton.clicked.connect(self.find)
        self.layout.addWidget(self.findbutton, 0, 6, 5, 1)

        self.findallbutton = QtGui.QPushButton("Find All")
        self.findallbutton.clicked.connect(self.findall)
        self.layout.addWidget(self.findallbutton, 5, 6, 5, 1)

        self.replacebutton = QtGui.QPushButton("Replace")
        self.replacebutton.clicked.connect(self.replace)
        self.layout.addWidget(self.replacebutton, 10, 6, 5, 1)

        self.replaceallbutton = QtGui.QPushButton("Replace All")
        self.replaceallbutton.clicked.connect(self.replaceall)
        self.layout.addWidget(self.replaceallbutton, 15, 6, 5, 1)

    #     HELPERS

    @logger.call('gui', 'debug')
    def find(self):
        self.table.find()
        self.hide()

    @logger.call('gui', 'debug')
    def findall(self):
        '''Exec QDialog with found indexes in QTableWidget'''

        indexes = self.table.findall()
        horizontalheaders = self.table.get_horizontal_headers()
        dialog = ReportFindAll(self, indexes, horizontalheaders)
        self.hide()
        dialog.exec_()

    @logger.call('gui', 'debug')
    def replace(self):
        self.table.replace()
        self.hide()

    @logger.call('gui', 'debug')
    def replaceall(self):
        '''Extract matched indexes and exec QMessageBox instance'''

        counts = self.table.replaceall()
        self.hide()
        self.exec_msg(text='{0} values were replaced'.format(sum(counts)),
            windowTitle='Replace All Summary',
            parent=self)
