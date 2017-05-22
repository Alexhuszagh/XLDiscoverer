'''
    Gui/Views/Crosslink_Discoverer/settings/peptide
    _______________________________________________

    Widget to edit peptide search settings for Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.chemical import proteins
from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.utils import logger

from . import base


# SECTIONS
# --------


@logger.init('gui', 'DEBUG')
class MowseSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Mowse Database"

    def __init__(self, parent):
        super(MowseSection, self).__init__(parent)

        self.protein_interval()
        self.peptide_interval()
        self.add_spacer()

    #    ITEMS

    def protein_interval(self):
        '''Sets the default protein interval for the Mowse database'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Protein Interval")
        hlayout.addWidget(label)

        storage = updating.Storage('protein_interval')
        interval = updating.SpinBox(self, storage,
            minimum=1e3,
            maximum=1e5,
            tooltip="Bin width for grouping proteins in the Mowse database",
            width=100,
            suffix=' Da')
        hlayout.addWidget(interval)

    def peptide_interval(self):
        '''Sets the default peptide interval for the Mowse database'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Peptide Interval")
        hlayout.addWidget(label)

        storage = updating.Storage('peptide_interval')
        interval = updating.SpinBox(self, storage,
            minimum=1e2,
            maximum=1e4,
            tooltip="Bin width for grouping peptide in the Mowse database",
            width=100,
            suffix=' Da')
        hlayout.addWidget(interval)


@logger.init('gui', 'DEBUG')
class ProteaseSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Proteases"
    _layout = QtGui.QGridLayout

    def __init__(self, parent):
        super(ProteaseSection, self).__init__(parent)

        self.enzyme()
        self.non_specific()
        self.peptide_length()
        self.missed_cleavages()
        self.add_spacer()

    #    ITEMS

    def enzyme(self):
        '''Sets the currently active proteolytic enzyme for peptide cleavage'''

        label = widgets.Label("Enzyme")
        self.layout.addWidget(label, 1, 0, 1, 5)

        values = sorted(proteins.ENZYMES)
        storage = updating.Storage('current_enzyme')
        enzyme = updating.ComboBox(self, values, storage,
            tooltip='Proteolytic enzyme used prior to mass spectrometry')
        self.layout.addWidget(enzyme, 1, 5, 1, 5)

    def non_specific(self):
        '''Sets the default non-specific cleavage sites for the experiment'''

        label = widgets.Label("Non-Specific")
        self.layout.addWidget(label, 2, 0, 1, 5)

        values = ['0', 'N', 'C', '1', '2']
        storage = updating.Storage('nonspecific_cleavage')
        nonspecific = updating.ComboBox(self, values, storage,
            tooltip='Non-specific cleavage sites during proteolytic cleavage')
        self.layout.addWidget(nonspecific, 2, 5, 1, 5)

    def peptide_length(self):
        '''Sets the minimum peptide length for spectral searching'''

        label = widgets.Label("Peptide Length Range")
        self.layout.addWidget(label, 3, 0, 1, 5)

        storage = updating.Storage('minimum_peptide_length')
        minimum = updating.SpinBox(self, storage,
            minimum=3,
            maximum=10,
            tooltip="Minimum peptide length included during spectral searches",
            width=50)
        self.layout.addWidget(minimum, 3, 8, 1, 1)

        storage = updating.Storage('maximum_peptide_length')
        maximum = updating.SpinBox(self, storage,
            minimum=20,
             maximum=70,
            tooltip="Maximum peptide length included during spectral searches",
            width=50)
        self.layout.addWidget(maximum, 3, 9, 1, 1)

    def missed_cleavages(self):
        '''Sets the minimum missed cleavages during spectral searching'''

        label = widgets.Label("Missed Cleavage Range")
        self.layout.addWidget(label, 4, 0, 1, 5)

        storage = updating.Storage('minimum_missed_cleavages')
        minimum = updating.SpinBox(self, storage,
            minimum=0,
            maximum=5,
            tooltip="Minimum number of missed cleavages from "
            "proteolytic digestion",
            width=50)
        self.layout.addWidget(minimum, 4, 8, 1, 1)

        storage = updating.Storage('maximum_missed_cleavages')
        maximum = updating.SpinBox(self, storage,
            minimum=0,
            maximum=10,
            tooltip="Maximum number of missed cleavages from "
            "proteolytic digestion",
            width=50)
        self.layout.addWidget(maximum, 4, 9, 1, 1)


# PANES
# -----


@logger.init('gui', 'DEBUG')
class PeptidesPane(base.BaseSettings):
    '''Definitions for peptide settings'''

    def __init__(self, parent):
        super(PeptidesPane, self).__init__(parent)

        self.layout.addWidget(MowseSection(self))
        self.layout.addWidget(ProteaseSection(self))
