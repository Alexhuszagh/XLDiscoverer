'''
    Export/Spreadsheet/single
    _________________________

    Base object for generating spreadsheet data rows.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import types

from collections import namedtuple

from xldlib.export import formats
from xldlib.general import sequence
from xldlib.resources.parameters import reports
from xldlib.utils import logger
from xldlib.xlpy.tools import frozen

from . import base


# DATA
# ----

NONSINGLE_TYPES = [
    'Intersubunit',
    'Intrasubunit',
    'Double',
    'Deadend',
    'Intralink',
    'Ambiguous'
]

# FORMATTING
# ----------

CLASSES = [
    ('Protein Mods', formats.ProteinModifications),
    ('Peptide', formats.ModificationsInPeptide)
]

# OBJECTS
# -------


@sequence.serializable('Single')
class Single(namedtuple("Single", "index frozen name type")):
    '''Subclass for automatic defaults'''

    def __new__(cls, index, frozen, *args, **kwds):
        if len(args) < 2:
            kwds.setdefault('type', reports.LINKTYPES['single'])
        if len(args) < 1:
            kwds.setdefault('name', reports.LINKNAMES['Incomplete'])

        return super(Single, cls).__new__(cls, index, frozen, *args, **kwds)


# SINGLES
# -------


@logger.init('spreadsheet', 'DEBUG')
class CreateSingleData(base.SpreadsheetData):
    '''
    Processes the spreadsheet data for a "single", that is, a peptide
    with a crosslinker fragment but which does not mass back to
    any known bridging mode (deadend, intralink, interlink) in the parent.
    '''

    def __init__(self, row):
        super(CreateSingleData, self).__init__(row)

        source = self.app.discovererthread
        self.reporterions = source.reporterions
        self.freezer = frozen.SingleFreezer(row)

        self.processing = {}
        for column, cls in CLASSES:
            self.processing[column] = cls(row)

    def __call__(self):
        '''Returns the spreadsheet data as a dictionary'''

        indexes = self.getnocrosslinkindexes()
        for index in indexes:
            values = base.RowValues()

            self.spreadsheetrow.setattrs(values)
            self.spreadsheetrow.setdata(values, [index])
            self.setcrosslinktypes(values)
            self.setcrosslinkdata(values, [index])
            self.setprocessing(values, [index])

            if self.reporterions:
                self.spreadsheetrow.setreporter(values, [index])
            else:
                self.spreadsheetrow.setreporternull(values, [index])

            frozen = self.freezer(index, values)
            self.row.data['singles'].append(Single([index], frozen))
            self.row.data['spreadsheet']['singles'].append(values)

    #    SETTERS

    def setcrosslinktypes(self, values):
        '''Sets the crosslink type as solely a single'''

        for key in NONSINGLE_TYPES:
            values[key] = ''
        values['Single'] = 'T'

    def setcrosslinkdata(self, values, index):
        '''Sets the generic crosslinker data'''

        values['XL'] = position = list(self.fragments(index))
        values['Subunit Names'] = self.formatsubunits(index)
        values['Linkage Info'] = self.formatlinkage(position, index)
        values['Linear'] = self.formatlinear(index)
        values['xiNet'] = self._xinet(index, position)

    def setprocessing(self, values, index):
        '''Uses processing functions to store custom data displays'''

        for column, inst in self.processing.items():
            value = inst(index)
            if isinstance(value, types.GeneratorType):
                value = list(value)
            values[column] = value

    #    GETTERS

    def getnocrosslinkindexes(self):
        '''Returns the indexes without crosslinks'''

        indexes = set(range(len(self.row.data['matched']['id'])))
        for crosslink in self.row.data['crosslinks']:
            indexes.difference_update(crosslink.index)

        return sorted(indexes)
