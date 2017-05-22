'''
    Gui/Views/Crosslink_Discoverer/Proteins/tabs
    ____________________________________________

    Tabs with embedded tables for the proteins editor.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import weakref

from PySide import QtCore, QtGui

from xldlib.controllers import bindings
from xldlib.gui.views import widgets
from xldlib.gui.views.dialogs import findreplace
from xldlib.objects import protein
from xldlib.qt.objects import base
from xldlib.qt import resources as qt
from xldlib.utils import logger



# DELEGATE
# --------


@logger.init('gui', 'DEBUG')
class ProteinModelDelegate(QtGui.QItemDelegate):
    '''Centers items during paints events'''

    def paint(self, painter, option, index):
        '''Paints the QTableView with centered items'''

        text = index.model().data(index, QtCore.Qt.DisplayRole)
        options = QtGui.QStyleOptionViewItemV4(option)
        options.displayAlignment = qt.ALIGNMENT['Center']

        self.drawDisplay(painter, options, options.rect, text)
        self.drawFocus(painter, options, options.rect)


# TABLE
# -----


@logger.init('gui', 'DEBUG')
class ProteinsTable(widgets.BaseTableView, bindings.Keys):
    '''
    Definitions for a Protein table.
    Reimplements showEvent() to call a constructor for the first instance.
    '''

    def __init__(self, parent, key):
        super(ProteinsTable, self).__init__(parent)

        self.key = key
        self.finder = findreplace.FindReplace(self)

        self.set_properties()
        self.set_widget_styles()

    #    PROPERTIES

    @property
    def tabs(self):
        return self.parent().parent()

    @property
    def section(self):
        return self.tabs.parent()

    @property
    def view(self):
        return self.section.parent()

    #  EVENT HANDLING

    def showEvent(self, event):
        '''Call constructor on show'''

        if self.tabs.proteins.path is not None:
            self._show()
        event.accept()

    def hideEvent(self, event):
        '''Calls a finisher to update the current HDF5 storage'''

        self.submit()
        self.finish()
        event.accept()

    def dragEnterEvent(self, event):
        event.accept()

    def dragMoveEvent(self, event):
        event.accept()

    def dropEvent(self, event):
        '''Sets the data from the drag'''

        data = event.mimeData()
        row = self.rowAt(event.pos().y())
        column = self.columnAt(event.pos().x())
        if data.hasText():
            self.item(row, column).setText(data.text())

    #    SETTERS

    def set_properties(self):
        '''Sets the default widget policies for the QTable'''

        self.setAcceptDrops(True)
        self.bind_table()

        delegate = ProteinModelDelegate(self)
        self.setItemDelegate(delegate)

        self.set_size_policy('Expanding', 'Expanding')

    def set_model(self):
        '''Sets the model for the QTableView'''

        model = self.tabs.model
        if model.database().isOpen():
            model.change_table(self.key)
            self.setModel(model)

            # show active columns
            for column in range(model.columnCount()):
                self.showColumn(column)

            # hide inactive columns
            for column in model.hidden[self.key]:
                self.hideColumn(column)

    #    PUBLIC

    def paste(self, *args):
        '''Checks if the database is open prior to forcing any queries'''

        if self.model() is not None and self.model().database().isOpen():
            self.model().paste(*args)

    def clearContents(self):
        '''Set the unloaded and call the default clearContents method'''

        super(ProteinsTable, self).clearContents()

    def submit(self):
        '''Forces submits only with an active database'''

        if self.model() is not None and self.model().database().isOpen():
            self.model().submit_all()

    def finish(self):
        self.setModel(protein.ProteinModel())

    #    HELPERS

    def showspinner(self):
        self.section.loaddialog.show()
        self.app.processEvents()

    def hidespinner(self):
        self.section.loaddialog.hide()
        self.app.processEvents()

    def _show(self):
        '''Add data to the current table from the array'''

        # show the dialog
        self.showspinner()
        self.set_model()

        # finish and cleanup
        self.hidespinner()


# TABS
# ----

TABS = [
    'Blacklist',
    'Greylist',
    'Named',
    'Decoys',
    'Depricated',
    'Proteins',
]


@logger.init('gui', 'DEBUG')
class TableTabs(QtGui.QTabWidget, base.BaseObject):
    '''Definitions for table tab widgets'''

    def __init__(self, parent, proteins):
        super(TableTabs, self).__init__(parent)

        self.proteins = weakref.proxy(proteins)
        self.tables = []
        self.load()

    @property
    def current_tab(self):
        return self.tables[self.currentIndex()]

    #      SETTERS

    def set_model(self):
        '''Sets the QSqlTableModel for the QTableViews'''

        self.model = protein.ProteinModel(None, self.proteins.db)
        self.model.setEditStrategy(protein.ProteinModel.OnManualSubmit)

    def settables(self):
        '''Sets the tables on initialization or resetting'''

        for name in TABS:
            page = ProteinsTable(self, name.lower())
            self.addTab(page, name)
            self.tables.append(page)

    #      HELPERS

    def load(self):
        self.set_model()
        self.settables()

    def submit(self):
        self.tables[self.currentIndex()].submit()

    def saveas(self, path):
        '''Commits all changes to file and then saves the proteins'''

        self.submit()
        self.proteins.saveas(path)

    def finish(self):
        '''Finished the current tab view and closes the SQL connections'''

        self.submit()
        self.cleartables()

        del self.model

    def cleartables(self):
        '''Clears the shown tables upon a a file change event'''

        while self.tables:
            self.tables.pop()
            index = len(self.tables)
            self.removeTab(index)

    def updatetables(self):
        self.cleartables()
        self.settables()

    def loadvisible(self):
        self.current_tab.show()

    def refresh(self):
        tab = self.current_tab
        tab.hide()
        tab.show()
