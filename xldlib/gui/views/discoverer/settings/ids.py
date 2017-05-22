'''
    Gui/Views/Crosslink_Discoverer/Settings/ids
    ___________________________________________

    Widget to edit identification settings for Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.utils import logger

from . import base


# WIDGETS
# -------


class DisablableCheckBox(updating.CheckBox):
    '''Updating QCheckbox which greys out and disactivates'''

    def __init__(self, widget, *args, **kwds):
        super(DisablableCheckBox, self).__init__(*args, **kwds)

        self.widget = widget
        self.widget.stateChanged.connect(self.toggle_enabled)
        self.toggle_enabled()

    #    PUBLIC

    def toggle_enabled(self):
        '''Toggles the current widget clickstate'''

        if self.widget.isChecked():
            self.disable()
        else:
            self.enable()

    def disable(self):
        '''Disables the checkbox and disables the setting'''

        if self.isEnabled():
            self.setEnabled(False)
            self.oldstate = self.isChecked()
            self.item = False

    def enable(self):
        '''Disables the checkbox and disables the setting'''

        if not self.isEnabled():
            self.setEnabled(True)
            self.item = self.oldstate

            del self.oldstate


class DisablableComboBox(updating.ComboBox):
    '''Updating QComboBox which greys out and disactivates'''

    def __init__(self, widget, *args, **kwds):
        super(DisablableComboBox, self).__init__(*args, **kwds)

        self.widget = widget
        self.widget.stateChanged.connect(self.toggle_enabled)
        self.toggle_enabled()

    #    PUBLIC

    def toggle_enabled(self):
        '''Toggles the current widget clickstate'''

        if self.widget.isChecked():
            self.setEnabled(False)
        else:
            self.setEnabled(True)


class DisablableLabel(widgets.Label):
    '''Updating QLabel which greys out and disactivates'''

    def __init__(self, widget, text):
        super(DisablableLabel, self).__init__(text)

        self.widget = widget
        self.widget.stateChanged.connect(self.toggle_enabled)
        self.toggle_enabled()

    #    PUBLIC

    def toggle_enabled(self):
        '''Toggles the current widget clickstate'''

        if self.widget.isChecked():
            self.setEnabled(False)
        else:
            self.setEnabled(True)


# SECTIONS
# --------


@logger.init('gui', 'DEBUG')
class SearchHitSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Search Hits"

    def __init__(self, parent):
        super(SearchHitSection, self).__init__(parent)

        self.include()
        self.best_hit()
        self.add_spacer()

    #    ITEMS

    def include(self):
        '''Include all or filter search hits.'''

        storage = updating.Storage('all_search_hits')
        self.include_all = updating.CheckBox("All Search Hits", self, storage,
            tooltip="Include all search hits or select only the best.")

        self.layout.addWidget(self.include_all)

    def best_hit(self):
        '''Key for best hit selection when filtering search hits'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = DisablableLabel(self.include_all, "Best Hit")
        hlayout.addWidget(label)

        storage = updating.Storage('best_hit_key')
        values = ['Rank', 'Score']
        best_hit = DisablableComboBox(self.include_all, self, values, storage,
            tooltip="Parameter used to select best search hit.")
        hlayout.addWidget(best_hit)


@logger.init('gui', 'DEBUG')
class AmbiguitySection(base.BaseSection):
    '''Section for processing ambiguous identifications'''

    # SECTION
    # -------
    _title = "Ambiguous Identifications"

    def __init__(self, parent):
        super(AmbiguitySection, self).__init__(parent)

        self.cluster()
        self.expand()
        self.add_spacer()

    #  PROPERTIES

    @property
    def include_all(self):
        return self.parent().search_hits.include_all

    #    ITEMS

    def cluster(self):
        '''Sets whether to cluster identifications by product scan'''

        storage = updating.Storage('cluster_product_scans')
        cluster = DisablableCheckBox(self.include_all,
            "Cluster Ambiguous", self, storage,
            tooltip="Cluster ambiguous identifications from the same scan"
            "prior to link searching.")

        self.layout.addWidget(cluster)

    def expand(self):
        '''Sets how to expand the ambiguous identifiations'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = DisablableLabel(self.include_all, "Expand Ambiguous")
        hlayout.addWidget(label)

        storage = updating.Storage('expand_ambiguous')
        values = ['None', 'Interesting', 'All']
        expand = DisablableComboBox(self.include_all, self, values, storage,
            tooltip="Crosslink expansion after link searching from "
            "ambiguous identifications clustered to the same product scan.")
        hlayout.addWidget(expand)


# PANES
# -----


@logger.init('gui', 'DEBUG')
class IdentificationsPane(base.BaseSettings):
    '''Definitions for identification settings'''

    def __init__(self, parent):
        super(IdentificationsPane, self).__init__(parent)

        self.search_hits = SearchHitSection(self)
        self.layout.addWidget(self.search_hits)
        self.layout.addWidget(AmbiguitySection(self))
