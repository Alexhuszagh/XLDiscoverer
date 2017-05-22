'''
    XlPy/MS1Quantitation/integrate
    ______________________________

    Integrates the selected extracted ion chromatograms and adds the
    quantitative data to the spreadsheet data.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from collections import defaultdict

from xldlib.definitions import ZIP
from xldlib.qt.objects import base
from xldlib.utils import logger


# OBJECTS
# -------


@logger.init('quantitative', 'DEBUG')
class IntegrateXics(base.BaseObject):
    '''
    Iterates over each set of spreadsheets to store the integrated XICs
    to each spreadsheet row
    '''

    def __init__(self, document, matched=None):
        super(IntegrateXics, self).__init__()

        self.document = document
        self.matched = matched

        self.profile = document.getattr('profile')
        self.memo = defaultdict(dict)

    @logger.call('quantitative', 'debug')
    def __call__(self):
        '''Integrates the XICs over the transitions and matched document'''

        for row, transitionfile in enumerate(self.document):
            if self.matched is not None:
                self.setmatchedrow(row, transitionfile)
            else:
                self.setdocumentrow(transitionfile)

    #  CLASS METHODS

    @classmethod
    def fromthread(cls):
        '''Initializes the integrator from a Transitions document'''

        source = IntegrateXics.app.discovererthread
        return cls(source.transitions, source.matched)

    #     SETTERS

    def setmatchedrow(self, row, transitionfile):
        '''Sets all the integrated XIC data for the matched and XIC row'''

        self.setdocumentrow(transitionfile)

        zipped = self.getzipped(row)
        frozen_labels = {i.getattr('frozen'): i for i in transitionfile}
        for spreadsheet, crosslink in zipped:
            labels = frozen_labels[crosslink.frozen]
            self.setspreadsheet(spreadsheet, labels)

    def setdocumentrow(self, transitionfile):
        '''Sets all the integrated XIC data for the document row'''

        for labels in transitionfile:
            labels.set_integrated()

    @staticmethod
    def setspreadsheet(spreadsheet, labels):
        '''Sets the integrated MS1 data for the spreadsheet from the labels'''

        defaultsheet = labels.getattr('spreadsheet')
        keys = set(defaultsheet) - set(spreadsheet)
        for key in keys:
            spreadsheet[key] = defaultsheet[key]

    #    GETTERS

    def getzipped(self, row):
        '''Custom zipper which uses the labeledcrosslinks indexes'''

        data = self.matched[row]
        spreadsheets = data['spreadsheet']['labeled']
        crosslinks = data['labeledcrosslinks']
        return ZIP(spreadsheets, crosslinks)
