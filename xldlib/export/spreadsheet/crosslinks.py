'''
    Export/Spreadsheet/crosslinks
    _____________________________

    Generates the spreadsheet data for a individually sequenced crosslinks.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import types

from xldlib.utils import logger

from . import base
from .. import formats

# FORMATTING
# ----------

CLASSES = [
    ('Protein Mods', formats.ProteinModifications),
    ('Peptide', formats.ModificationsInPeptide),
    ('Linear w/ Mods', formats.ToSkyline)
]


# CROSSLINKS
# ----------


@logger.init('spreadsheet', 'DEBUG')
class CreateCrosslinkData(base.SpreadsheetData):
    '''
    Processes the spreadsheet data for an identified (sequenced
    or predicted via isotope labels) link
    '''

    def __init__(self, row):
        super(CreateCrosslinkData, self).__init__(row)

        source = self.app.discovererthread
        self.crosslinkers = source.parameters.crosslinkers
        self.isobaric = source.parameters.isobaric
        self.reporterions = source.reporterions

        self.processing = {}
        for column, cls in CLASSES:
            self.processing[column] = cls(row)

    @logger.call('spreadsheet', 'debug')
    def __call__(self, crosslink):
        '''Returns the spreadsheet data as a dictionary'''

        values = base.RowValues()

        self.spreadsheetrow.setattrs(values)
        self.spreadsheetrow.setdata(values, crosslink.index)
        self.setcrosslinkdata(values, crosslink)
        self.setprocessing(values, crosslink)

        if self.reporterions:
            self.spreadsheetrow.setreporter(values, crosslink.index)
        else:
            self.spreadsheetrow.setreporternull(values, crosslink.index)

        return values

    #    SETTERS

    @logger.call('spreadsheet', 'debug')
    def setcrosslinkdata(self, values, crosslink):
        '''Sets the crosslinker data'''

        values.update(crosslink.tospreadsheet())
        values.update(self.formatcrosslinktypes(crosslink).tospreadsheet())

        values['XL'] = position = list(self.fragments(crosslink.index))
        values['Subunit Names'] = self.formatsubunits(crosslink.index)
        values['Linkage Info'] = self.formatlinkage(position, crosslink.index)
        values['Linear'] = self.formatlinear(crosslink.index)
        values['xiNet'] = self._xinet(crosslink.index, position)

    @logger.call('spreadsheet', 'debug')
    def setprocessing(self, values, crosslink):
        '''Uses processing functions to store custom data displays'''

        for column, inst in self.processing.items():
            value = inst(crosslink)
            if isinstance(value, types.GeneratorType):
                value = list(value)
            values[column] = value

    #   FORMATTERS

    @logger.call('spreadsheet', 'debug')
    def formatcrosslinktypes(self, crosslink):
        '''0 -> LinkTypes(intersubunit="T", ...)'''

        intrasubunit = self.getintrasubunit(crosslink.index)
        return crosslink.totypes(intrasubunit)
