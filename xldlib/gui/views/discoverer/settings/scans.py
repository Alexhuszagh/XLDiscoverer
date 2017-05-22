'''
    Gui/Views/Crosslink_Discoverer/settings/scans
    _____________________________________________

    Widget to edit scan settings for Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.utils import logger

from . import base


# SECTIONS
# --------


@logger.init('gui', 'DEBUG')
class LinkingSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Linking"

    def __init__(self, parent):
        super(LinkingSection, self).__init__(parent)

        self.verify()
        self.scan_steps()
        self.precursor_intensity()
        self.add_spacer()

    #    ITEMS

    def verify(self):
        '''Sets a checkbox for whether to verify the precursor scan or not'''

        storage = updating.Storage('check_precursor')
        verify = updating.CheckBox("Verify Precursor", self, storage,
            tooltip="Verify the precursor m/z exists in precursor scan")

        self.layout.addWidget(verify)

    def scan_steps(self):
        '''Sets the scan steps for precursor scan linking'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Max Steps")
        hlayout.addWidget(label)

        storage = updating.Storage('precursor_scan_steps')
        steps = updating.SpinBox(self, storage,
            minimum=5,
            maximum=1000,
            tooltip="Maximum scans preceeding the identified product scan\n"
            "to search for the precursor scan.",
            width=75)
        hlayout.addWidget(steps)

    def precursor_intensity(self):
        '''Sets the minimum intensity required for precursor matching'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Max Missing Precursors")
        hlayout.addWidget(label)

        storage = updating.Storage('missing_precursor_threshold')
        intensity = updating.SpinBox(self, storage,
            minimum=0,
            maximum=100,
            tooltip="Maximum number (percent) of product scans without\n"
            "linked precursor scans before reporting mismatched files.",
            suffix='%',
            width=75)
        hlayout.addWidget(intensity)


@logger.init('gui', 'DEBUG')
class LevelsSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Levels"

    def __init__(self, parent):
        super(LevelsSection, self).__init__(parent)

        self.precursor_level()
        self.product_level()
        self.add_spacer()

    #    ITEMS

    def precursor_level(self):
        '''Sets the MS level for the precursor scan data'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Precursor")
        hlayout.addWidget(label)

        storage = updating.Storage('precursor_scan_level')
        level = updating.SpinBox(self, storage,
            minimum=2,
            maximum=10,
            tooltip="Precursor Scan Level",
            prefix='MS',
            width=75)
        hlayout.addWidget(level)

    def product_level(self):
        '''Sets the MS level for the product scan data'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Product")
        hlayout.addWidget(label)

        storage = updating.Storage('product_scan_level')
        level = updating.SpinBox(self, storage,
            minimum=2,
            maximum=10,
            tooltip="Product Scan Level",
            prefix='MS',
            width=75)
        hlayout.addWidget(level)


# PANES
# -----


@logger.init('gui', 'DEBUG')
class ScansPane(base.BaseSettings):
    '''Definitions for scan settings'''

    def __init__(self, parent):
        super(ScansPane, self).__init__(parent)

        self.layout.addWidget(LinkingSection(self))
        self.layout.addWidget(LevelsSection(self))
