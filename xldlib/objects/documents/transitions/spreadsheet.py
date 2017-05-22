'''
    Objects/Documents/Transitions/spreadsheet
    _________________________________________

    Adds quantitative labels to a given spreadsheet data set.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import ast
import types

from xldlib.export import formats, spreadsheet
from xldlib.qt.objects import base
from xldlib.utils import logger, masstools, serialization

# DATA
# ----

GENERAL_DATA = [
    'Ambiguous',
    'Common/Gene Name',
    #'Cross-Linker',
    'Cross-Link Number',
    'DB Peptide',
    'Deadend',
    'Double',
    'File Name',
    'Intersubunit',
    'Intralink',
    'Intrasubunit',
    'Linear',
    'Linkage Info',
    'MS Scans Name',
    'MS1 Scans Name',
    'MS2 PPM',
    'MS2 PPM Corrected',
    'MS2 z',
    'MS3 EV',
    'MS3 PPM',
    'MS3 Score',
    'MS3 m/z',
    'MS3 z',
    'Matched Output Name',
    'Missing Mass',
    'Precursor RT',
    'Precursor Scan',
    'Precursor Scans Name',
    'Product Scan',
    'Product Scans Name',
    'Project Name',
    'Runtime',
    'Search Name',
    'Search Rank',
    'Single',
    'Start',
    'Subunit',
    'Subunit Name',
    'Subunit Names',
    'XL',
    'xiNet'
]

CLASSES = [
    ('Protein Mods', formats.LabeledProteinModifications),
    ('Peptide', formats.LabeledModificationsInPeptide),
    ('Linear w/ Mods', formats.LabeledToSkyline)
]


# OBJECTS
# -------


@serialization.register('QuantitativeRow')
class QuantitativeRow(spreadsheet.RowValues):
    '''Subclass with custom serialization methods'''

    def __init__(self, *args, **kwds):
        kwds.setdefault('labeled', True)
        super(QuantitativeRow, self).__init__(*args, **kwds)

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, obj):
        data = {ast.literal_eval(k): v for k, v in obj['data'].items()}
        return cls(data, labeled=obj['labeled'])

    #      MAGIC

    @serialization.tojson
    def __json__(self):
        '''Implementation to dump an object as a msgpack'''

        return {
            'data': {str(k): v for k, v in self.items()},
            'labeled': self.labeled
        }


# FORMATTER
# ---------


@logger.init('document', 'DEBUG')
class Formatter(base.BaseObject):
    '''
    Formats the spreadsheet data to add quantitative labels and
    add isotopic-labeled data and fields.
    '''

    def __init__(self, row):
        super(Formatter, self).__init__()

        self.row = row
        self.processing = {}

        source = self.app.discovererthread
        self.profile = source.parameters.profile
        self.crosslinkers = source.parameters.crosslinkers

    def __call__(self, labeledcrosslink):
        '''Formats the spreadsheet to add isotopic labels to the headers'''

        out = QuantitativeRow()
        spreadsheet = labeledcrosslink.getspreadsheet(self.row.data)

        self.setdata(labeledcrosslink)
        self.setgeneral(out, spreadsheet, labeledcrosslink)
        self.setlabelspecific(out, spreadsheet, labeledcrosslink)

        return out

    #    SETTERS

    def setdata(self, labeledcrosslink):
        '''Sets the processing class data isntances'''

        source = self.app.discovererthread
        row = source.files[labeledcrosslink.file]
        for column, cls in CLASSES:
            self.processing[column] = cls(row)

    def setgeneral(self, out, spreadsheet, labeledcrosslink):
        '''
        Sets the precursor data, which does not change between the
        isotopic states.
        '''

        for key in GENERAL_DATA:
            out[(' ', key)] = spreadsheet[key]

        baseheader = self.profile.getheader(labeledcrosslink.sequenced)
        out[(' ', 'Cross-Linker')] = baseheader

    def setlabelspecific(self, out, spreadsheet, labeledcrosslink):
        '''Sets the label-specific data columns for the spreadsheet'''

        for label in labeledcrosslink.states:
            header = self.profile.getheader(label.populations)
            out[(header, 'MS2 m/z')] = self.getmz(label, spreadsheet)

            for column, inst in self.processing.items():
                value = inst(label, spreadsheet, labeledcrosslink)
                if isinstance(value, types.GeneratorType):
                    value = list(value)
                out[(header, column)] = value

    #    GETTERS

    def getmz(self, label, spreadsheet):
        '''Returns the m/z value for the given label'''

        charge = spreadsheet['MS2 z'][0]
        return masstools.mz(label.mass, charge, 0)
