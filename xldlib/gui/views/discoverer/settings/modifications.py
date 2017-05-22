'''
    Gui/Views/Crosslink_Discoverer/Settings/modifications
    _____________________________________________________

    Widget to edit modification settings for Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import json

from PySide import QtGui

from xldlib.general import mapping
from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.qt import resources as qt
from xldlib.resources import chemical_defs
from xldlib.utils import logger
from xldlib.utils.io_ import qtio

from . import base


# OBJECTS
# -------


class ModificationSelectionIo(object):
    '''Definitions for spectral I/O events involving modification selections'''

    def __init__(self, parent, constant, variable):
        super(ModificationSelectionIo, self).__init__()

        self.parent = parent
        self.constant = constant
        self.variable = variable

    #      I/O

    def load(self, title='Load Modifications...'):
        '''Gets a load path the load the document from file'''

        path = qtio.getopenfile(self.parent, title)
        try:
            if path:
                self._load(path)
        except (AssertionError, ValueError):
            self.parent.exec_msg(windowTitle='Error',
                text='Modification selection file not recognized')

    def _load(self, path, keys=('constant', 'variable')):
        '''Load modifications from file'''

        with open(path) as f:
            document = json.load(f)

        assert all(i in document for i in keys)
        for key in keys:
            items = chemical_defs.MODIFICATIONS.loaditems(*document[key])
            getattr(self, key).attribute = items

    def save(self, title='Save Modifications...'):
        '''Path checker which then calls the save method'''

        path = qtio.getsavefile(self.parent, title)
        if path:
            self._save(path)

    def _save(self, path, keys=('constant', 'variable')):
        '''Dumps modifications to file'''

        document = {k: getattr(self, k).modifications for k in keys}
        with open(path, 'w') as f:
            json.dump(document, f)


# WIDGETS
# -------


class ModificationView(widgets.ListWidget, updating.BaseStorage):
    '''Definitions for a modifications view with selectable items'''

    def __init__(self, parent, store, engine):
        super(ModificationView, self).__init__(parent)

        self._store = store
        self.engine = engine
        self._lookup = mapping.BidirectionalDict()

        self.set_styles()
        self.set_data()
        self.set_selection()

        self.itemSelectionChanged.connect(self.update_selection)

    #   PROPERTIES

    @property
    def lookup(self):
        return self._lookup

    @property
    def attribute(self):
        return self.data[self.key]

    @attribute.setter
    def attribute(self, value):
        self.data[self.key] = value
        self.set_selection()

    @property
    def ids(self):
        return [self.lookup(i) for i in self.selected]

    @property
    def modifications(self):
        return [chemical_defs.MODIFICATIONS[i] for i in self.ids]

    #    SETTERS

    def set_styles(self):
        '''Sets the default style representations for the QListWidget'''

        self.setMaximumHeight(qt.INCREMENT)
        self.setSelectionMode(qt.SELECTION_MODE['Multi'])

    def set_data(self):
        '''Fills the widget with the modification entries'''

        engine = self.engine.currentText()
        modificationids = chemical_defs.MODIFICATIONS.get_engine(engine)

        counter = 0
        for modificationid in modificationids:
            modification = chemical_defs.MODIFICATIONS[modificationid]
            if not modification.fragment:
                name = modification.tostr()
                self.addItem(name)

                self.lookup[modificationid] = counter
                counter += 1

    def set_selection(self):
        '''Sets the widget selection from a list of 1-indexed rows'''

        self.block_once(self.clearSelection)
        selection = self.selectionModel()
        model = self.model()
        for index in self.attribute:
            modelindex = model.createIndex(self.lookup[index], 0)
            selection.select(modelindex, qt.SELECTION_MODEL['Select'])

    #    UPDATERS

    def update_data(self):
        self.block_once(self.clear)
        del self.attribute[:]
        self.lookup.clear()
        self.set_data()

    def update_selection(self):
        # cannot call self.set_selection
        self.data[self.key] = self.ids

# SECTIONS
# --------


@logger.init('gui', 'DEBUG')
class PeptideSearchSection(base.BaseSection):
    '''Section for setting peptide search parameters'''

    # SECTION
    # -------
    _title = "Peptide Search"

    def __init__(self, parent):
        super(PeptideSearchSection, self).__init__(parent)

        self.database()
        self.maximum_crosslinkers()
        self.minimum_crosslinker()
        self.add_spacer()

        self.constant_modifications()
        self.variable_modifications()
        self.add_spacer()
        self.io = ModificationSelectionIo(self, self.constant, self.variable)

        self.profile()
        self.add_spacer()

    #    ITEMS

    def database(self):
        '''Sets the current spectral engine for the modification selection'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Database")
        hlayout.addWidget(label)

        storage = updating.Storage('modification_engine')
        values = ['Protein Prospector', 'Mascot', 'Proteome Discoverer']
        self.engine = updating.ComboBox(self, values, storage,
            tooltip='Current modification database for modification selection')
        self.engine.currentIndexChanged.connect(self.reset_database)

        hlayout.addWidget(self.engine)

    def maximum_crosslinkers(self):
        '''Sets the maximum crosslinker fragments per peptide'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Max Crosslinkers")
        hlayout.addWidget(label)

        storage = updating.Storage('maximum_crosslinkers')
        crosslinkers = updating.SpinBox(self, storage,
            minimum=0,
            maximum=10,
            tooltip="Maximum number of crosslinker fragments per peptide.",
            width=75)
        hlayout.addWidget(crosslinkers)

    def minimum_crosslinker(self):
        '''Sets the maximum modifications fragments per peptide'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Max Modifications")
        hlayout.addWidget(label)

        storage = updating.Storage('maximum_modifications')
        modifications = updating.SpinBox(self, storage,
            minimum=0,
            maximum=10,
            tooltip="Maximum number of modifications per peptide.",
            width=75)
        hlayout.addWidget(modifications)

    def constant_modifications(self):
        '''Creates a QListWidget to select constant modifications'''

        header = widgets.Label("Constant", font=qt.BOLD_FONT)
        self.layout.addWidget(header)

        storage = updating.Storage('constant_modifications')
        self.constant = ModificationView(self, storage, self.engine)
        self.layout.addWidget(self.constant)

    def variable_modifications(self):
        '''Creates a QListWidget to select variable modifications'''

        header = widgets.Label("Variable", font=qt.BOLD_FONT)
        self.layout.addWidget(header)

        storage = updating.Storage('variable_modifications')
        self.variable = ModificationView(self, storage, self.engine)
        self.layout.addWidget(self.variable)

    def profile(self):
        '''Defines the current modification profiles for saving purposes'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        load = widgets.ClickButton("Load Mods", self.io.load)
        hlayout.addWidget(load)

        save = widgets.ClickButton("Save Mods", self.io.save)
        hlayout.addWidget(save)

    def reset_database(self):
        '''Resets the current view'''

        self.constant.update_data()
        self.variable.update_data()


# PANES
# -----


@logger.init('gui', 'DEBUG')
class ModificationsPane(base.BaseSettings):
    '''Definitions for modification settings'''

    def __init__(self, parent):
        super(ModificationsPane, self).__init__(parent)

        self.layout.addWidget(PeptideSearchSection(self))
