'''
    Export/Spreadsheet/base
    _______________________

    Inheritable methods between spreadsheet data-processing classes.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import Sequence

import six

from xldlib.definitions import ZIP
from xldlib.export import formats
from xldlib.qt.objects import base
from xldlib.utils import logger, modtools, serialization

from . import spreadsheetrow


# OBJECTS
# -------


@serialization.register('RowValues')
@logger.init('spreadsheet', 'debug')
class RowValues(dict):
    '''Definitions for spreadsheet row storage'''

    def __init__(self, *args, **kwds):
        self.labeled = kwds.pop('labeled', False)
        super(RowValues, self).__init__(*args, **kwds)

    #     MAGIC

    @serialization.tojson
    def __json__(self):
        return {
            'data': dict(self),
            'labeled': self.labeled
        }

    #  CLASS METHODS

    @classmethod
    def loadjson(cls, data):
        return cls(data['data'], labeled=data['labeled'])

    #     PUBLIC
    #    GETTERS

    def getsearch(self):
        return self.getvalue('Search Name')[0]

    def getcrosslinker(self):
        return self.getvalue('Cross-Linker')

    def getlinkage(self):
        return self.getvalue('Linkage Info') or tuple(self.getvalue('XL'))

    def getids(self):
        return tuple(self.getvalue('Subunit'))

    def getnames(self):
        return tuple(self.getvalue('Common/Gene Name'))

    def getpeptide(self):
        return self.getvalue('DB Peptide')

    def getstart(self):
        return self.getvalue('Start')

    def getscore(self):
        return tuple(self.getvalue('MS3 Score'))

    def getev(self):
        return tuple(self.getvalue('MS3 EV'))

    def getkey(self, key):
        if self.labeled:
            key = (' ', key)
        return key

    def getvalue(self, *keys):
        '''Returns all items in the passes keys, adjusting for labeling'''

        if len(keys) == 1:
            return self.get(self.getkey(keys[0]))
        else:
            return [self.get(key) for key in map(self.getkey, keys)]

    #    SETTERS

    def setids(self, ids):
        self[self.getkey('XL')] = tuple(ids)


@logger.init('spreadsheet', 'debug')
class SpreadsheetData(base.BaseObject):
    '''Inheritable methods for spreadsheet data processing'''

    def __init__(self, row):
        super(SpreadsheetData, self).__init__()

        self.row = row
        self.spreadsheetrow = spreadsheetrow.SpreadsheetRow(row)
        self._xinet = formats.ToXiNet(row)

        source = self.app.discovererthread
        isobaric = source.parameters.isobaric.todict()
        self.fragments = modtools.FragmentPositions(row, isobaric)

    #    GETTERS

    @logger.call('spreadsheet', 'debug')
    def getintrasubunit(self, names):
        '''Returns whether the crosslink is intrasubunit'''

        # use the preferred names over the UniProt ID, since we want
        # different IDs for redundant proteins to be mapped to the same
        # sequence
        if (isinstance(names, Sequence) and
            isinstance(names[0], six.integer_types)):
            names = self.row.data.getcolumn(names, 'preferred')
        else:
            names = iter(names)
        name = next(names)

        return all(i == name for i in names)

    #   FORMATTERS

    @logger.call('spreadsheet', 'debug')
    def formatsubunits(self, indexes):
        '''
        Makes "Subunit Names" column data, with either reporting a
        single protein (if all are identical) or proteins with a "-"
        delimiter.
            formatsubunits([0, 1]) -> ['Rpn11', 'Rpn11'] -> 'Rpn11'
            formatsubunits([0, 2]) -> ['Rpn11', 'Rpn2']  -> 'Rpn11-Rpn2'
        '''

        names = list(self.row.data.getcolumn(indexes, 'preferred'))
        if self.getintrasubunit(names):
            return names[0]

        else:
            return u'-'.join(names)

    @logger.call('spreadsheet', 'debug')
    def formatlinkage(self, fragmentpositions, indexes):
        '''
        Processes a linkage from the preferred name and the crosslinker
        positions.
            fragmentpositions -- list of ';'-joined res:pos values for
                crosslinker modified residues

            >>> self.process_linkage(['K37;K41;K42', 'K58'], [0, 1])
                'GAPDH:K37;K41;K42-GAPDH:K58'
        '''

        linkage = []
        names = self.row.data.getcolumn(indexes, 'preferred')
        zipped = ZIP(names, fragmentpositions)
        for name, position in zipped:
            linkage.append(u'{0}:{1}'.format(name, position))

        return u'-'.join(linkage)

    @logger.call('spreadsheet', 'debug')
    def formatlinear(self, indexes):
        '''
        Makes a linear peptide from the sequences comprising the link.
            indexes -- references to positions within the table
            >>> format_linear([0, 1]) ->'LESNKEGTRLKEEYQSLIR'
        '''

        peptides = self.row.data.getcolumn(indexes, 'peptide')
        return ''.join(peptides)
