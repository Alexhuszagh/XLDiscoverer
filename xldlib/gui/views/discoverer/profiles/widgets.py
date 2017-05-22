'''
    Gui/Views/Crosslink_Discoverer/Profiles/widgets
    _______________________________________________

    Contains the combobox widgets to toggle the profile selection.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import Counter

import six

from PySide import QtGui

import tables as tb

from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.qt import resources as qt
from xldlib.resources import chemical_defs, engines
from xldlib.utils import decorators, logger

from .base import TableChild, ViewChild


# PROFILES
# --------


class LineEdit(widgets.LineEdit):
    '''Subclass for signal/slot connections'''

    def __init__(self, parent, values):
        super(LineEdit, self).__init__(parent)

        self.setReadOnly(False)
        self.editingFinished.connect(self.checkunique)

        # avoids keeping the cache after changing item selection
        self.parent().activated.connect(self.clearstate)

    #  EVENT HANDLING

    def focusInEvent(self, event):
        '''On editing of the QcomboBox::lineEdit()'''

        event.accept()
        self.oldstate = self.text()

    #     PUBLIC

    def checkunique(self):
        '''Checks if the text is unique, and if not, edits the profile name'''

        current = self.text()
        oldstate = getattr(self, "oldstate", current)
        if current != oldstate:

            # set the unique value
            unique = self.parent().getunique(current)
            if unique != current:
                current = unique
                self.setText(current)

            self.parent().updatenames(oldstate, current)

        self.clearstate()

    #     HELPERS

    def clearstate(self):
        if hasattr(self, "oldstate"):
            del self.oldstate


@logger.init('gui', 'DEBUG')
class EditableProfileBox(updating.ComboBox, ViewChild):
    '''Editable, unique QComboBox definitions'''

    def __init__(self, parent, profiles, **kwds):
        self.names = self.getnames(profiles)
        values = self.getvalues(profiles)
        store = updating.Storage('current_isotope_profile')

        # new profile instance
        index = store.data[store.key]
        if index not in profiles:
            name = self.getunique('New')
            parent.new_profile(name=name, index=index)
            self.appendname(name, index)

        super(EditableProfileBox, self).__init__(parent, values, store, **kwds)

        self.setLineEdit(LineEdit(self, self.names))

    #  EVENT HANDLING

    def contextMenuEvent(self, event):
        '''On a QContextMenu show event'''

        menu = widgets.Menu(self)

        delete = QtGui.QAction("&Delete", self)
        menu.addAction(delete)

        action = menu.exec_(self.mapToGlobal(event.pos()))
        if action == delete:
            self.delete()

    #     PUBLIC

    def set_current_text(self, item):
        '''Sets current item based off of item value.'''

        if isinstance(item, six.integer_types):
            item = self.names(item)

        index = self.lookup[item]
        self.setCurrentIndex(index)

    @decorators.overloaded
    def store_value(self):
        '''Stores the values upon a value change'''

        # clean up the old profile, and remove template from profiles list
        # if it was a new entry
        self.profile.removenulls()
        if self.index not in chemical_defs.PROFILES:
            profile = self.parent().profiles.pop(self.index)
            self.removename(profile.name)

        self.index = self.get_index()
        self.parent().switch_profile()

    def new_profile(self, parent, index, name):
        '''Instantiates a new profile and binds to the parent profiles'''

        profile = chemical_defs.Profile.blank(name, self.parent().crosslinkers)
        self.profiles[index] = profile

    #    GETTERS

    def get_index(self):
        text = self.currentText()
        return self.names._names.get(text, max(chemical_defs.PROFILES)+1)

    @staticmethod
    def getnames(profiles):
        return tb.Enum({v.name: k for k, v in profiles.items()})

    def getvalues(self, profiles, name='New'):
        '''Returns the values along with a unique "New" identifier'''

        values = []
        newadded = False
        for id_, profile in profiles.items():
            if id_ in chemical_defs.PROFILES:
                values.append(profile.name)
            else:
                newadded = True
        if not newadded:
            values.append(self.getunique(name))
        return values

    def getunique(self, name):
        '''Returns the unique version of the name'''

        if name in self.names:
            counter = 1
            while '{0} {1}'.format(name, counter) in self.names:
                counter += 1
            return '{0} {1}'.format(name, counter)
        return name

    #    HELPERS

    def delete(self):
        '''Deletes the parent profile instance, updates the names and values'''

        # block signals
        self.block()

        # delete the profiles and any memos leftover
        self.parent().delete_profile()
        self.clear()
        self.lineEdit().clearstate()

        # update the names and lookup items, as well as the values
        self.names = self.getnames(self.parent().profiles)
        values = self.getvalues(self.parent().profiles)
        self.populate(values)

        # unblock signals
        self.block()
        self.parent().switch_profile()
        self.set_current_text(self.profile.name)

    def appendnew(self, name='New'):
        self.addItem(self.getunique(name))

    def appendname(self, name, index):
        '''Adds a name to the current self.names enum'''

        asdict = self.names._names
        asdict[name] = index
        self.names = tb.Enum(asdict)

    def removename(self, name, remove_value=False):
        '''Adds a name to the current self.names enum'''

        asdict = self.names._names
        del asdict[name]
        self.names = tb.Enum(asdict)

        if remove_value:
            index = self.lookup.pop(name)
            del self.values[index]

    def updatenames(self, oldkey, newkey):
        '''Updates the profile names upon the profile change'''

        index = self.names[oldkey]
        self.__updateenum(oldkey, newkey)
        self.__updateprofiles(index, newkey)
        self.__updateqcombo(oldkey, newkey)

    def __updateenum(self, oldkey, newkey):
        '''Updates the current enums'''

        asdict = self.names._names
        asdict[newkey] = asdict.pop(oldkey)
        self.names = tb.Enum(asdict)

    def __updateprofiles(self, index, name):
        '''Updates the current widget profiles'''

        profile = self.profile._replace(name=name)
        self.parent().profiles[index] = profile

        # only update the profiles if not a "New" entry
        if index in chemical_defs.PROFILES:
            chemical_defs.PROFILES[index] = profile

    def __updateqcombo(self, oldkey, newkey):
        '''Updates the QCombobox lookups'''

        self.lookup[newkey] = index = self.lookup.pop(oldkey)
        self.values[index] = newkey

        self.setItemText(index, newkey)


# ENGINES
# -------


@logger.init('gui', 'DEBUG')
class EngineBox(widgets.StylizedBox, ViewChild):
    '''Uneditable variant that allows toggling of the current search engine'''

    def __init__(self, parent, **kwds):
        super(EngineBox, self).__init__(parent)

        # no blank entries added
        self.addblank = False

        self.populate(sorted(engines.SEARCH))
        self.set_current_text(self.profile.engine)
        self.currentIndexChanged.connect(self.store_value)

    #     PUBLIC

    @decorators.overloaded
    def store_value(self):
        '''Stores the values upon a value change'''

        self.profile.engine = self.currentText()

        # downstream signals
        chemical_defs.PROFILE_EDITED_SIGNAL.emit(self.profile)
        self.parent().clear_table()


# DIMENSIONS
# ----------


class DimensionsBox(widgets.SpinBox, ViewChild):
    ''''Provides a QSpinBox to edit the number of available profiles'''

    def __init__(self, parent, **kwds):
        super(DimensionsBox, self).__init__(parent)

        self.setMinimum(1)
        self.setMaximum(6)

        self.setValue(len(self.profile.populations))

        self.valueChanged.connect(self.parent().resize)


# CROSSLINKERS
# ------------


@logger.init('gui', 'DEBUG')
class CrosslinkerBox(widgets.ListViewBox, TableChild):
    '''
    Uneditable variant with a memo and eventFilter to avoid having a
    condition not using a given crosslinker.
    '''

    def __init__(self, parent, population_index, crosslinker_id):
        super(CrosslinkerBox, self).__init__(parent)

        self.population_index = population_index
        self.initialize(crosslinker_id)
        self.activated.connect(self.store_value)

    #   PROPERTIES

    @property
    def population(self):
        return self.profile.populations[self.population_index]

    @population.setter
    def population(self, value):
        self.profile.populations[self.population_index] = value

    @property
    def crosslinker_id(self):
        return self.lookup[self.currentText()]

    @property
    def crosslinker(self):
        return chemical_defs.CROSSLINKERS[self.crosslinker_id]

    @property
    def name(self):
        return self.crosslinker.name

#    @property
#    def memo(self):
#        return self.parent().memo

    #    PUBLIC

    def initialize(self, crosslinker_id):
        '''Adds a single item (values are added dynamically)'''

        name = chemical_defs.CROSSLINKERS[crosslinker_id].name
        self.addItem(name)
        self.lookup = {name: crosslinker_id}
        self.setCurrentIndex(0)

    @decorators.overloaded
    def store_value(self):
        self.population.crosslinker = self.crosslinker_id

    #    GETTERS

    def getmemo(self):
        '''Returns a unique memo with all items'''

        memo = self.parent().memo.copy()
        for widget in self.parent().widgets:
            if widget != self:

                memo[widget.crosslinker_id] -= 1
                if not memo[widget.crosslinker_id]:
                    del memo[widget.crosslinker_id]

        return memo

    #    HELPERS

    def reset(self):
        '''Resets the QCombobox items from a memo'''

        # TODO: buig here, since the lookup starts at 0 but the
        # CROSSLINKERS starts at 1.... Check the github repository to
        # see how to patch it
        # ->
        memo = self.getmemo()
        self.lookup = {chemical_defs.CROSSLINKERS[i].name: i for i in memo}
        names = sorted(self.lookup)

        self.clear()
        for name in names:
            self.addItem(name)

        index = names.index(self.name)
        self.setCurrentIndex(index)


@logger.init('gui', 'DEBUG')
class CrosslinkerBoxWidget(QtGui.QWidget, ViewChild):
    '''Provides a widget parent for QComboBoxes with an eventFilter'''

    def __init__(self, parent):
        super(CrosslinkerBoxWidget, self).__init__(parent)

        self.widgets = []

        self.set_layout(QtGui.QHBoxLayout)
        self.set_view()

    #   PROPERTIES

    @property
    def memo(self):
        return Counter(self.profile.crosslinker_ids)

    @property
    def crosslinkers(self):
        return set(self.profile.crosslinkers)

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

    #    SETTERS

    def set_view(self):
        '''Sets the initial view'''

        for index, population in enumerate(self.profile.populations):
            box = CrosslinkerBox(self, index, population.crosslinker)
            box.installEventFilter(self)

            self.layout.addWidget(box)
            self.widgets.append(box)

    #    HELPERS

    def reset_view(self):
        '''Resets the view upon a profile change'''

        while self.widgets:
            self.widgets.pop().deleteLater()
        self.set_view()

