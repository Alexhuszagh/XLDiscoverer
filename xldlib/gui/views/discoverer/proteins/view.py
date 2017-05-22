'''
    Gui/Views/Crosslink_Discoverer/Proteins/view
    ____________________________________________

    Main view for the protein tables.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os

from PySide import QtCore, QtGui

from xldlib.controllers import messages
from xldlib.definitions import partial
from xldlib.gui.views.dialogs import contextbar, save
from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.objects import protein
from xldlib.qt import resources as qt
from xldlib.resources import paths
from xldlib.utils import logger
from xldlib.utils.io_ import qtio, threads, typechecker

from . import dbwidgets, dialog, iterators, tabs

# CONSTANTS
# ---------

SAVE_TABLE = 'Save table as...'
OPEN_FASTA = 'Add From Fasta...'
OPEN_UNIPROT_XML = 'Add From UniProt XML...'


# CONTEXTS
# --------


class ProteinContext(contextbar.ContextBar):
    _windowkey = 'table'


# RETURN
# ------


@logger.init('gui', 'DEBUG')
class ButtonSection(widgets.KeyBindingWidget):
    '''Provides a button section to return to the previous view'''

    def __init__(self, parent):
        super(ButtonSection, self).__init__(parent)

        self.set_layout(QtGui.QVBoxLayout)
        self.set_widgets()

    #     SETTERS

    def set_widgets(self):
        '''Sets the target widgets for the layout'''

        self.layout.addWidget(widgets.Divider(self))

        done = widgets.ClickButton("Done Editing", self.parent().close)
        self.layout.addWidget(done)


# LOADING
# -------


@logger.init('gui', 'DEBUG')
class LoadingSection(widgets.KeyBindingWidget, messages.BaseMessage):
    '''Provides a button section to load, save, and initialize new templates'''

    def __init__(self, parent):
        super(LoadingSection, self).__init__(parent)

        self.proteins = protein.ProteinTable()
        self.loaddialog = save.IoDialog(mode='load', parent=self)
        self.savedialog = save.IoDialog(parent=self)
        self.download = dialog.UniProtDialog(self)
        self.threading = threads.IoThreading(self.parent)

        self.set_layout(QtGui.QVBoxLayout)
        self.set_widgets()

        self.is_valid_file()

    #    PROPERTIES

    @property
    def path(self):
        return paths.DYNAMIC['current_proteins']

    @path.setter
    def path(self, value):
        paths.DYNAMIC['current_proteins'] = value
        self.database.store_from_value(value)

    def get_dbpath(self):
        return getattr(self, "_dbpath", None)

    def set_dbpath(self, value):
        self._dbpath = value

    dbpath = property(get_dbpath, set_dbpath)

    #     SETTERS

    def set_widgets(self):
        '''Sets the target widgets for the layout'''

        self.__set_loadfile()
        self.__set_ioevents()
        self.layout.addWidget(widgets.Divider(self))
        self.__set_addbuttons()
        self.add_spacer()

        self.__set_limiteddatabase()
        self.add_spacer()

        self.__set_tabs()

    def __set_loadfile(self):
        '''Adds a QLineEdit to toggle the currently open database'''

        layout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Current Database ")
        layout.addWidget(label)

        storage = updating.Storage('current_proteins', paths.DYNAMIC)
        self.database = updating.LineEdit(self, storage,
            tooltip="Path to current database.")
        self.database.value_about_to_change.connect(self.set_dbpath)
        self.database.value_changed.connect(self.is_valid_file)
        layout.addWidget(self.database)

        item = dbwidgets.DatabaseItem("Get Database", self.database, self)
        layout.addWidget(item)

    def __set_ioevents(self):
        '''Adds new/save initializers for the database'''

        layout = self.add_layout(QtGui.QHBoxLayout)

        self.newbutton = widgets.ClickButton("New Database", self.new)
        layout.addWidget(self.newbutton)

        self.saveasbutton = widgets.ClickButton("Save As", self.saveas)
        layout.addWidget(self.saveasbutton)

    def __set_addbuttons(self):
        '''Adds buttons to the current widget'''

        layout = self.add_layout(QtGui.QHBoxLayout)

        self.addfasta = widgets.ClickButton("Add Fasta", self.add_from_fasta)
        layout.addWidget(self.addfasta)

        self.addxml = widgets.ClickButton("Add UniProt XML", self.add_from_xml)
        layout.addWidget(self.addxml)

        server = widgets.ClickButton("Add from Server", self.download.show)
        layout.addWidget(server)

    def __set_limiteddatabase(self):
        '''Sets the limited database status for the current proteins object'''

        layout = self.add_layout(QtGui.QHBoxLayout)
        self.add_spacer(layout)

        label = widgets.Label("Limited Database: ")
        layout.addWidget(label)

        self.limited = dbwidgets.LimitedDatabaseComboBox(self,
            self.proteins,
            tooltip="Select a limited or automatically generated database")
        layout.addWidget(self.limited)
        self.add_spacer(layout)

    def __set_tabs(self):
        '''Initializes a QTabWidget where each tab contains'''

        self.tabs = tabs.TableTabs(self, self.proteins)
        self.layout.addWidget(self.tabs)

    #     HELPERS

    def load(self):
        '''Loads the widget and the views on initializing'''

        self.loaddialog.show()
        self.app.processEvents()
        self.threading(self.proteins.ioload, self.loaddialog, self.load_items)

    def load_items(self):
        '''Main thread executation of the display widgets'''

        self.set_layout(QtGui.QVBoxLayout)
        self.set_widgets()
        self.is_valid_file()

    def finish(self):
        self.tabs.finish()
        self.proteins.close()

    def new(self, title=SAVE_TABLE):
        '''Initiates a new ProteinTable from a new file path'''

        path = self.getpath(qtio.getsavefile, title)
        if path:
            # close and initialize a new object at the path
            self.finish()
            self.proteins.new(path)
            self.tabs.load()
            self.path = path

    def saveas(self, title=SAVE_TABLE):
        '''Saves the current database to a new path'''

        path = self.getpath(qtio.getsavefile, title)
        if path:
            self.savedialog.show()
            self.app.processEvents()

            fun = partial(self.tabs.saveas, path)
            connect = partial(setattr, self, path)
            self.threading(fun, self.savedialog, connect)

    def toggle_enabled(self, enabled):
        '''Toggles the enabled widgets based on if the database is valid'''

        self.saveasbutton.setEnabled(enabled)
        self.limited.setEnabled(enabled)
        self.tabs.setEnabled(enabled)

        if enabled:
            self.limited.set_text()

    def is_valid_file(self):
        '''Checks if the database is a valid file'''

        path = self.database.text()
        enabled = os.path.exists(path) and typechecker.sqlite(path)
        if path != self.dbpath:
            if enabled:
                self.finish()
                self.proteins.open()
                self.tabs.load()
                self.tabs.loadvisible()

        self.toggle_enabled(enabled)
        self.tabs.refresh()

    #     ADDERS

    def add_from_fasta(self, title=OPEN_FASTA, path=None):
        '''Add items to the protein database from a FASTA entry'''

        text = qtio.getopenfile(self, title, path)
        if text:
            self.add_items(iterators.UniProtFastaIterator(text))

    def add_from_xml(self, title=OPEN_UNIPROT_XML, path=None):
        '''Add items to the protein database from a UniProt XML'''

        text = qtio.getopenfile(self, title, path)
        if text:
            self.add_items(iterators.UniProtXmlIterator(text))

    def add_from_server(self):
        '''Adds items from a given server query'''

        iterator = iterators.UniProtServerIterator()
        self.add_items(iterator, inputmode='taxonomic identifier')

    def add_items(self, iterator, inputmode='file'):
        '''Flanks the add items call with a loading dialog'''

        self.tabs.submit()

        self.loaddialog.show()
        try:
            self._add_items(iterator)
            self.loaddialog.hide()
        except AssertionError:
            self.loaddialog.hide()
            self.exec_msg(windowTitle='ERROR',
                text='Invalid {} specified'.format(inputmode))

    def _add_items(self, iterator):
        '''Adds items using a given iterator to a the active database'''

        model = self.tabs.current_tab.model()
        for offset, protein_obj in enumerate(iterator):
            model.addprotein(protein_obj)


# PROTEINS VIEW
# -------------


@logger.init('gui', 'DEBUG')
class ProteinsView(widgets.KeyBindingWidget):
    '''
    View with a set of tab widgets with bound QTableWidgets, along
    with various other parameters.

    Each tab, upon the showEvent(), loads the QTableWidget data from
    the HDF5 storage class.
    '''

    # SIGNALS
    # -------
    closed = QtCore.Signal(object)

    def __init__(self, parent):
        super(ProteinsView, self).__init__(parent)

        self.set_layout(QtGui.QVBoxLayout, alignment='Top')
        self.set_widgets()
        self.set_context()

        self.show()

    #     SETTERS

    def set_widgets(self):
        '''Sets the target widgets for the layout'''

        self.loading = LoadingSection(self)
        self.layout.addWidget(self.loading)

        buttons = ButtonSection(self)
        self.layout.addWidget(buttons)

    def set_context(self):
        '''Adds a context bar to the current window'''

        self.context = ProteinContext(self, qt.TABLE_BAR)
        self.bind_keys({'Ctrl+?': self.context.show})

    #  EVENT HANDLING

    def closeEvent(self, event):
        '''Shows the parent menu widget upon a close event'''

        self.loading.finish()
        self.closed.emit(self)
        event.accept()
