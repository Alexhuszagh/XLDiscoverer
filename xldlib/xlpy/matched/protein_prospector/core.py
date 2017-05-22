'''
    XlPy/Matched/Protein_Prospector/core
    ____________________________________

    Objects which parse different Protein Prospector file formats
    and are the engines the process the matched data.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import codecs
import copy
import six
import xml.sax

from xldlib.definitions import re
from xldlib.objects import matched
from xldlib.utils import logger
from . import modifications
from .. import base, csv_, pepxml

# load objects/functions
from collections import namedtuple


# PEPXML
# ------


@logger.init('matched', 'DEBUG')
class ParseXml(base.MatchedPeptideBase):
    '''Processes data from the pep.XML format of Protein Prospector'''

    def __init__(self, row):
        super(ParseXml, self).__init__(row)

        self.handler = pepxml.PepXmlHandler(row)
        self.parser = xml.sax.make_parser()
        self.parser.setContentHandler(self.handler)

    @logger.call('matched', 'debug')
    def __call__(self):
        '''On start'''

        self.parser.parse(self.fileobj)
        self.fileobj.close()

        self.setids()
        self.setfileheader()

    #     SETTERS

    def setfileheader(self):
        '''
        Stores the project and search names identically since the
        search name is typically missing.
        '''

        fraction = self.handler.start._fraction
        self.row.data['attrs']['project'] = fraction
        self.row.data['attrs']['search'] = fraction


# CONSTANTS
# ---------

HEADER = r'^(?:{})?Search Name:\t(.*)/(.*)\r?\n$'
if six.PY2:
    HEADER = HEADER.format(codecs.BOM_UTF8)
else:
    HEADER = HEADER.format(codecs.BOM_UTF8.decode('utf-8'))


# OBJECTS
# -------


class Modification(namedtuple("Modification", "string peptide "
    "start certain uncertain neutralloss")):

    def __new__(cls, string, peptide, start, **kwds):
        for key, value in matched.MODIFICATION_TEMPLATE.items():
            kwds.setdefault(key, copy.deepcopy(value))

        return super(Modification, cls).__new__(cls, string, peptide,
                                                start, **kwds)

    def todict(self):
        return matched.Modification({
            'certain': self.certain,
            'uncertain': self.uncertain,
            'neutralloss': self.neutralloss
        })


# CSV
# ---


@logger.init('matched', 'DEBUG')
class ParseCsv(base.MatchedPeptideBase):
    '''Processes data from matched scans to dictionary from a file object'''

    # REGEXP
    # ------
    header = re.compile(HEADER)

    def __init__(self, row):
        super(ParseCsv, self).__init__(row)

        self.csv = csv_.CSVUtils(row)
        self.csv.process['modifications'] = self.getmodification
        self.modparser = modifications.ModificationParser(row)

    @logger.call('matched', 'debug')
    def __call__(self):
        '''
        Finds search name from Protein Prospector output,
        finds dataframe and dumps to dictionary of lists, where the
        keys are columns and lists values.
        '''

        self.setfileheader()
        header = self.row.engines['matched'].defaults.header - 1
        while header:
            self.fileobj.readline()
            header -= 1

        self.csv.set_reader(self.fileobj)
        self.csv()
        self.setids()

    #     SETTERS

    def setfileheader(self):
        '''Grabs the search and project names from the header line.'''

        match = self.header.match(self.fileobj.readline())
        self.row.data['attrs']['project'] = match.group(1).strip()
        self.row.data['attrs']['search'] = match.group(2).strip()

    #     GETTERS

    def getmodification(self, unparsed):
        '''Returns the parsed modification from the unparsed string'''

        peptide = self.row.data['matched']['peptide'][-1]
        start = self.row.data['matched']['start'][-1]

        # parse the modification
        if isinstance(unparsed, list):
            unparsed = unparsed[0]
        modification = Modification(unparsed, peptide, start)
        self.modparser(modification)

        return modification.todict()

