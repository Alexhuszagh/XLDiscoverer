'''
    Gui/Views/Crosslink_Discoverer/Profiles/view
    ____________________________________________

    Contains the core widgets for the current profile selection.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.definitions import partial
from xldlib.gui.views.widgets import Label, Widget
from xldlib.resources import chemical_defs
from xldlib.resources.parameters import defaults
from xldlib.utils import logger

from . import table, widgets


# VIEW
# ----


@logger.init('gui', 'DEBUG')
class ProfileSelectionView(Widget):
    '''View with a bound list of profiles, and various dependent widgets'''

    def __init__(self, parent):
        super(ProfileSelectionView, self).__init__(parent)

        self.set_profiles()
        self.set_size_policy('Expanding', 'Expanding')
        self.set_layout(QtGui.QGridLayout)

        self.set_profile_selection()
        self.set_engines()
        self.set_dimensions()
        self.set_crosslinkers()
        self.set_table()

    #    PROPERTIES

    @property
    def index(self):
        return defaults.DEFAULTS['current_isotope_profile']

    @index.setter
    def index(self, value):
        defaults.DEFAULTS['current_isotope_profile'] = max(value, 0)

    @property
    def profile(self):
        '''Returns the currently active profile or initiates a new one'''

        if self.index in self.profiles:
            return self.profiles[self.index]
        else:
            return self.set_new_profile()

    @profile.setter
    def profile(self, value):
        self.profiles[self.index] = value

    #     SETTERS

    def set_profiles(self):
        '''Sets the current profiles and crosslinker selection'''

        self.crosslinkers = chemical_defs.CROSSLINKERS.selected_ids
        self.profiles = chemical_defs.PROFILES.selected_profiles

    def set_profile_selection(self):
        '''Creates an updating QComboBox for the current profile'''

        label = Label("Select Profile: ")
        self.layout.addWidget(label, 0, 2)

        self.profile_combo = widgets.EditableProfileBox(self, self.profiles)
        self.layout.addWidget(self.profile_combo, 0, 5)

    def set_engines(self):
        '''Toggles the current search engine for the isotope profile'''

        label = Label("Select Search Engine: ")
        self.layout.addWidget(label, 1, 2)

        self.engine_qcombo = widgets.EngineBox(self)
        self.layout.addWidget(self.engine_qcombo, 1, 5)

    def set_dimensions(self):
        '''Adds a SpinBox to toggle the current dimensions'''

        label = Label("Conditions: ")
        self.layout.addWidget(label, 2, 2)

        self.number = widgets.DimensionsBox(self)
        self.layout.addWidget(self.number, 2, 5)

    def set_crosslinkers(self):
        '''Adds crosslinker boxes to a horizontal layout'''

        self.crosslinkerbox = widgets.CrosslinkerBoxWidget(self)
        self.layout.addWidget(self.crosslinkerbox, 3, 0, 1, 10)

    def set_table(self):
        '''Adds the QTableWidget to the current layout'''

        self.table = table.TableView(self)
        self.layout.addWidget(self.table, 4, 0, 1, 10)

    def set_new_profile(self, name=None, index=None):
        '''Instantiates and returns a new profile instance'''

        if name is None:
            name = self.profile_combo.values[-1]
        if index is None:
            index = self.index
        self.profile_combo.appendname(name, index)

        return self.new_profile(name, index)

    #     HELPERS

    def new_profile(self, name, index=None):
        '''Instantiates and returns a new profile instance'''

        if index is None:
            index = self.index
        profile = chemical_defs.Profile.blank(name, self.crosslinkers)
        self.profiles[index] = profile

        return profile

    def delete_profile(self):
        '''Deletes the currently active profile'''

        index = self.index
        if index in chemical_defs.PROFILES:
            del chemical_defs.PROFILES[index]
            del self.profiles[index]

            # since it has reindexing, need to reset the current profiles
            self.set_profiles()
            self.index = index

    def switch_profile(self):
        '''Switches the profile upon changing the selected QComboBox'''

        profile = self.profile
        fun = partial(self.engine_qcombo.set_current_text, profile.engine)
        self.engine_qcombo.block_once(fun)

        numberfun = partial(self.number.setValue, len(profile.populations))
        self.number.block_once(numberfun)

        self.crosslinkerbox.reset_view()
        self.table.reset_view()

    def clear_table(self):
        '''Clears the table upon a widget signal'''

        self.profile.clear()
        self.table.reset_view()

    def resize(self):
        '''Resizes the widget and adjusts the table'''

        self.profile.resize(self.number.value())
        self.crosslinkerbox.reset_view()
        self.table.reset_view()
