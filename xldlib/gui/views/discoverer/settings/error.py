'''
    Gui/Views/Crosslink_Discoverer/settings/error
    _____________________________________________

    Widget to edit error threshold settings for Crosslink Discoverer.

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
class ThresholdsSection(base.BaseSection):
    '''Section for setting search error thresholds'''

    # SECTION
    # -------
    _title = "Thresholds"

    def __init__(self, parent):
        super(ThresholdsSection, self).__init__(parent)

        self.isotopes()
        self.ppm()
        self.mass()
        self.add_spacer()

    #    ITEMS

    def isotopes(self):
        '''Sets the number of isotopes to match above monoisotopic'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Isotopes")
        hlayout.addWidget(label)

        storage = updating.Storage('isotope_threshold')
        isotopes = updating.SpinBox(self, storage,
            minimum=0,
            maximum=10,
            tooltip="Number of Isotopes above monoisotopic for the intact "
            "bridge to be sequenced at.",
            width=75)
        hlayout.addWidget(isotopes)

    def ppm(self):
        '''Sets the maximum PPM error at a given isotope'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("PPM")
        hlayout.addWidget(label)

        storage = updating.Storage('ppm_threshold')
        ppm = updating.SpinBox(self, storage,
            minimum=0,
            maximum=100,
            tooltip="Maximum relative error between the experimental and "
            "theoretical peptide mass.",
            width=75)
        hlayout.addWidget(ppm)

    def mass(self):
        '''Sets the low-resolution mass threshold for a link identification'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Mass")
        hlayout.addWidget(label)

        storage = updating.Storage('mass_threshold')
        mass = updating.SpinBox(self, storage,
            minimum=0,
            maximum=10000,
            tooltip="Maximum mass error for a low-resolution "
            "identification (low confidence).",
            width=100,
            suffix=' Da',
            singleStep=100)
        hlayout.addWidget(mass)


@logger.init('gui', 'DEBUG')
class ChargeSection(base.BaseSection):
    '''Section for setting search charge relaxation thresholds'''

    # SECTION
    # -------
    _title = "Charges"

    def __init__(self, parent):
        super(ChargeSection, self).__init__(parent)

        self.charge_relaxation()
        self.add_spacer()

    #    ITEMS

    def charge_relaxation(self):
        '''Sets the default order for the comparative report'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Relax Charge Matching")
        hlayout.addWidget(label)

        storage = updating.Storage('relax_charges')
        values = ['None', 'Standard', 'Low Confidence']
        relax = updating.ComboBox(self, values, storage,
            tooltip="Relax forced charge matches for\n"
            "Standard, Low Confidence, or no interlinks.")
        hlayout.addWidget(relax)


# PANE
# ----


@logger.init('gui', 'DEBUG')
class ErrorsPane(base.BaseSettings):
    '''Definitions for error threshold settings'''

    def __init__(self, parent):
        super(ErrorsPane, self).__init__(parent)

        self.layout.addWidget(ThresholdsSection(self))
        self.layout.addWidget(ChargeSection(self))
