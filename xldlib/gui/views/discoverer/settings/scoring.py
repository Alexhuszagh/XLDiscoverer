'''
    Gui/Views/Crosslink_Discoverer/settings/scoring
    _______________________________________________

    Widget to edit minimum scoring settings for Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.utils import decorators, logger

from . import base


# SPINBOXES
# ---------


class ScoreSpinBox(updating.DoubleSpinBox):
    '''Definitions for a scoring spinbox'''

    @decorators.overloaded
    def set_value(self):
        key, attrname = self.key
        value = getattr(self.data[key], attrname) / self.adjust
        self.setValue(value)

    @decorators.overloaded
    def store_value(self):
        '''Stores the values upon a value change'''

        key, attrname = self.key
        value = self.value() * self.adjust
        setattr(self.data[key], attrname,  value)
        self.data.edited.emit(key)


class EvSpinBox(updating.ScientificSpinBox):
    '''Definitions for an expectation value (EV) spinbox'''

    @decorators.overloaded
    def set_value(self):
        key, attrname = self.key
        value = getattr(self.data[key], attrname) / self.adjust
        self.setValue(value)

    @decorators.overloaded
    def store_value(self):
        '''Stores the values upon a value change'''

        key, attrname = self.key
        value = self.value() * self.adjust
        setattr(self.data[key], attrname,  value)
        self.data.edited.emit(key)


# SECTIONS
# --------


@logger.init('gui', 'DEBUG')
class ProteinProspectorSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Protein Prospector"

    def __init__(self, parent):
        super(ProteinProspectorSection, self).__init__(parent)

        self.protein_scores()
        self.peptide_scores()
        self.protein_ev()
        self.peptide_ev()
        self.add_spacer()

    #    ITEMS

    def protein_scores(self):
        '''Sets the minimum Protein Prospector protein score'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Min Protein Score")
        hlayout.addWidget(label)

        storage = updating.Storage(('Protein Prospector Score', 'protein'))
        score = ScoreSpinBox(self, storage,
            minimum=0.1,
            maximum=100,
            tooltip="Minimum protein score from database searching to be\n"
            "included in XL Discoverer searches.",
            width=75)
        hlayout.addWidget(score)

    def peptide_scores(self):
        '''Sets the minimum Protein Prospector peptide score'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Min Peptide Score")
        hlayout.addWidget(label)

        storage = updating.Storage(('Protein Prospector Score', 'peptide'))
        score = ScoreSpinBox(self, storage,
            minimum=0.1,
            maximum=100,
            tooltip="Minimum peptide score from database searching to be\n"
            "included in XL Discoverer searches.",
            width=75)
        hlayout.addWidget(score)

    def protein_ev(self):
        '''Sets the maximum Protein Prospector expectation value'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Max Protein EV")
        hlayout.addWidget(label)

        storage = updating.Storage(('Protein Prospector EV', 'protein'))
        expect = EvSpinBox(self, storage,
            minimum=1e-20,
            maximum=1,
            tooltip="Maximum protein EV from database searching to be\n"
            "included in XL Discoverer searches.",
            singleStep=0.01,
            width=75)
        hlayout.addWidget(expect)

    def peptide_ev(self):
        '''Sets the maximum Protein Prospector expectation value'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Max Peptide EV")
        hlayout.addWidget(label)

        storage = updating.Storage(('Protein Prospector EV', 'peptide'))
        expect = EvSpinBox(self, storage,
            minimum=1e-20,
            maximum=1,
            tooltip="Maximum peptide EV from database searching to be\n"
            "included in XL Discoverer searches.",
            singleStep=0.01,
            width=75)
        hlayout.addWidget(expect)


@logger.init('gui', 'DEBUG')
class MascotSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Mascot"

    def __init__(self, parent):
        super(MascotSection, self).__init__(parent)

        self.protein_scores()
        self.peptide_scores()
        self.protein_ev()
        self.peptide_ev()
        self.add_spacer()

    #    ITEMS

    def protein_scores(self):
        '''Sets the minimum Protein Prospector protein score'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Min Protein Score")
        hlayout.addWidget(label)

        storage = updating.Storage(('Mascot Score', 'protein'))
        score = ScoreSpinBox(self, storage,
            minimum=0.1,
            maximum=100,
            tooltip="Minimum protein score from database searching to be\n"
            "included in XL Discoverer searches.",
            width=75)
        hlayout.addWidget(score)

    def peptide_scores(self):
        '''Sets the minimum Protein Prospector peptide score'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Min Peptide Score")
        hlayout.addWidget(label)

        storage = updating.Storage(('Mascot Score', 'peptide'))
        score = ScoreSpinBox(self, storage,
            minimum=0.1,
            maximum=100,
            tooltip="Minimum peptide score from database searching to be\n"
            "included in XL Discoverer searches.",
            width=75)
        hlayout.addWidget(score)

    def protein_ev(self):
        '''Sets the maximum Protein Prospector expectation value'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Max Protein EV")
        hlayout.addWidget(label)

        storage = updating.Storage(('Mascot EV', 'protein'))
        expect = EvSpinBox(self, storage,
            minimum=1e-20,
            maximum=1,
            tooltip="Maximum protein EV from database searching to be\n"
            "included in XL Discoverer searches.",
            singleStep=0.01,
            width=75)
        hlayout.addWidget(expect)

    def peptide_ev(self):
        '''Sets the maximum Protein Prospector expectation value'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Max Peptide EV")
        hlayout.addWidget(label)

        storage = updating.Storage(('Mascot EV', 'peptide'))
        expect = EvSpinBox(self, storage,
            minimum=1e-20,
            maximum=1,
            tooltip="Maximum peptide EV from database searching to be\n"
            "included in XL Discoverer searches.",
            singleStep=0.01,
            width=75)
        hlayout.addWidget(expect)


# PANES
# -----


@logger.init('gui', 'DEBUG')
class ScoringPane(base.BaseSettings):
    '''Definitions for scoring settings'''

    def __init__(self, parent):
        super(ScoringPane, self).__init__(parent)

        self.layout.addWidget(ProteinProspectorSection(self))
        self.layout.addWidget(MascotSection(self))
