'''
    XlPy/MS1Quantitation/Isotope_Labels/finder
    __________________________________________

    Detects the isotope-labeled state of the peptide and then finds
    the labeled or unlabeled counterparts.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import copy
import operator as op
import weakref

from xldlib.objects.documents import transitions
from xldlib.onstart.main import APP
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults, reports
from xldlib.utils import logger
from xldlib.xlpy import wrappers

from . import labeler, matching


# DATA
# ----

QUANTIFIABLE_TYPES = [
    'interlink',
    'intralink',
    'deadend'
]


# FINDER
# ------


class Document(base.BaseObject):
    '''Wrapper for a transitions document'''

    def __init__(self, row):
        super(Document, self).__init__()

        self.row = row

        source = self.app.discovererthread
        self.document = weakref.proxy(source.transitions)
        self.globalsearch = self.document.getattr('global')

    #     MAGIC

    def iterfiles(self):
        '''Returns a custom iterator over the object'''

        if self.globalsearch:
            for item in self.document:
                yield item, item == self.row.transitions
        else:
            yield self.row.transitions, True

    def __getitem__(self, index):
        return self.document[index]


@logger.init('quantitative', 'DEBUG')
class FindLabeledCrossLinks(Document):
    '''
    Finds the isotope label category for each peptide, and then
    calculates the theoretical mod profile for all isotope-labeled
    variants of the cross-linked peptide and repacks a crosslinker
    for facile light/heavy calculations.

    Uses a set of two coroutines, one which is passed a data
    holder and the other which is passed a crosslink tuple.
    '''

    def __init__(self, row):
        super(FindLabeledCrossLinks, self).__init__(row)

        self.crosslinks = row.data['labeledcrosslinks']
        self.spreadsheets = self.row.data['spreadsheet']['labeled']

        source = self.app.discovererthread
        self.profile = source.parameters.profile
        self.experimental = matching.ModificationCounter()
        self.theoretical = matching.TheoreticalModifications(row)
        self.labeler = labeler.GetLabeledCrosslinks(row)
        self.formatter = transitions.Formatter(row)

        self.setlinktypes()

    def __call__(self):
        '''Iterates over all the crosslinks identified'''

        for index, crosslink in enumerate(self.row.data['crosslinks']):
            # include only selected linktypes, as defined in DEFAULTS
            if crosslink.type in self.linktypes:
                try:
                    self.addcrosslink(index, crosslink)
                except AssertionError:
                    pass

    #     ADDERS

    def addcrosslink(self, index, crosslink):
        '''
        Adds the crosslink label group if fully labeled to the matched
        data holder and creates an entry in the transitions file.
        Raises an AssertionError if no fully-labeled peptide is found.
        '''

        data = (self.getstate(i, crosslink) for i in crosslink.index)
        labeled = self.labeler(index, crosslink, data)

        if labeled is not None:
            self.crosslinks.append(labeled)
            spreadsheet = self.formatter(labeled)
            self.row.data['spreadsheet']['labeled'].append(spreadsheet)

            for file_, samefile in self.iterfiles():
                group = file_.addfromcrosslink(labeled, self.row.data)
                group.setattr('spreadsheet', copy.copy(spreadsheet))

                if samefile:
                    group.add_sequenced(labeled, 1)

    #     SETTERS

    def setlinktypes(self):
        '''Sets the unique linktypes to include during quantitation'''

        self.linktypes = set()
        for key in QUANTIFIABLE_TYPES:
            if defaults.DEFAULTS['quantify_' + key]:
                self.linktypes.add(reports.LINKTYPES[key])

    #     GETTERS

    def getstate(self, index, crosslink):
        '''Returns the isotope-labelled state for a given index'''

        # grab the experimental and theoretical modification profiles
        rowdata = self.row.data.getrow(index, asdict=True)
        experimental = self.experimental(rowdata)
        theoreticalprofiles = list(self.theoretical(rowdata))

        # iterate over and compare the theoretical and experimental,
        # if they are equal, then we've found an isotope-labeled mod
        # We also need to make sure the crosslinkers match (for d0/d12)
        # labeling, etc.
        for index, theoretical in enumerate(theoreticalprofiles):
            crosslinker = self.profile.populations[index].crosslinker

            if (experimental.counts == theoretical.counts and
                crosslinker == crosslink.crosslinker):
                return index, experimental, theoreticalprofiles

        # partial or incomplete labeling
        raise AssertionError("No theoretical profiles found")


# CORE
# ----


@logger.call('quantitative', 'debug')
@wrappers.runif(op.attrgetter('quantitative'))
@wrappers.threadprogress(60, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Finding isotope labeled crosslinks...")
def findisotopelabeled():
    '''Handler which calls the FindLabeledCrossLinks for all rows'''

    source = APP.discovererthread
    source.transitions.setglobal()

    source.transitions.setupmemo()
    for row in source.files:
        row.data.setdefault('labeledcrosslinks', [])

        labels = FindLabeledCrossLinks(row)
        labels()

    source.transitions.cleanupmemo()
