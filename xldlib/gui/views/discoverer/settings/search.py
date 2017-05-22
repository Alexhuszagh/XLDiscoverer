'''
    Gui/Views/Crosslink_Discoverer/settings/search
    ______________________________________________

    QTabWidget to select between panes for Crosslink Discoverer search
    settings.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.utils import logger

from . import error, modifications, ids, peptide, scans, scoring


# TABWIDGET
# ---------


@logger.init('gui', 'DEBUG')
class SearchSettings(QtGui.QTabWidget):
    '''Definitions for search settings'''

    def __init__(self, parent):
        super(SearchSettings, self).__init__(parent)

        self.addTab(scans.ScansPane(self), "Scans")
        self.addTab(peptide.PeptidesPane(self), "Peptides")
        self.addTab(error.ErrorsPane(self), "Errors")
        self.addTab(modifications.ModificationsPane(self), "Modifications")
        self.addTab(ids.IdentificationsPane(self), "Identifications")
        self.addTab(scoring.ScoringPane(self), "Scoring")
