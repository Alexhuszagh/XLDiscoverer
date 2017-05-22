'''
    XlPy/matched/parse
    __________________

    Links the proper matched scans file with the parsing engine, and
    intializes the parsers.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op
import os
import weakref

from functools import reduce

from xldlib.qt.objects import base
from xldlib.utils import logger
from xldlib.xlpy import wrappers

from . import mascot, positions, protein_prospector, proteins


# PARSERS
# -------

PARSERS = {
    "Protein Prospector": {
        "5.13.1, TEXT": protein_prospector.ParseCsv,
        "5.13.1, XML": protein_prospector.ParseXml
    },
    "Mascot": {
        "2.1.4, MIME": mascot.ParseMime,
        "2.1.4, XML": mascot.ParseXml
    },
    "Proteome Discoverer": {
        #"1.3SQLite": ParsePDSqlite3,
        #"1.3TabDelimited": ParsePDCsv,
        #"1.3PepXML": ParsePDPepXML
    }
}


def getparser(row):
    '''Instantiates the matched parser from a row object'''

    engine = row.data['attrs']['engines']['matched']
    cls = reduce(dict.get, engine, PARSERS)
    return cls(row)


# PARSER
# ------


@logger.init('matched', 'DEBUG')
class ParseMatchedScans(base.BaseObject):
    '''
    Identifies matched scan search database, and parses the
    matched scans to a readable format for Xl Discoverer.
    Appends each scan to a separate list (indexes for scan identifiers).
    '''

    def __init__(self, parent, row):
        super(ParseMatchedScans, self).__init__()

        self.parent = weakref.ref(parent)
        self.row = row
        self.parser = getparser(row)

    def parse(self):
        '''Initialize processing stage for the matched data'''

        self.parser()
        self._correcterrors()

    def process(self):
        '''
        Post-extraction processing to form the matched scans output,
        with indexes for each entry in self.source.matched[row]
        '''

        self.parser.remove()
        self.parent().positions(self.row)

        default = [1] * len(self.row.data['matched']['id'])
        self.row.data['matched'].setdefault('rank', default)

    #    HELPERS

    def _correcterrors(self):
        '''Corrects minor parsing errors in case of missing information'''

        # correct a potentially missing search parameter for Mascot files
        attrs = self.row.data['attrs']
        if attrs['search'] is None and attrs['fraction']:
            name, ext = os.path.splitext(os.path.basename(attrs['fraction']))
            attrs['search'] = name


# PARSER CONTROLLER
# -----------------


@logger.init('matched', 'DEBUG')
class ProcessMatchedData(base.BaseObject):
    '''
    Core class which processes the matched data initially, to grab
    a UniProt ID list to store gene sequences locally, filters
    false IDs, and then processes all search ranks (if applicable)
    to get a matched data holder for link searching.
    '''

    def __init__(self):
        super(ProcessMatchedData, self).__init__()

        self.source = weakref.proxy(self.app.discovererthread)
        self.ids = set()

        self.downloader = proteins.DownloadGenes(self.ids)
        self.positions = positions.ProcessPeptidePositions()

    @logger.call('matched', 'debug')
    @wrappers.threadprogress(10, 2, op.attrgetter('quantitative'))
    @wrappers.threadmessage("Parsing matched peptides...")
    def __call__(self):
        '''Initiates the scan parsers'''

        parsers = [ParseMatchedScans(self, row) for row in self.source.files]
        for parser in parsers:
            parser.parse()
            self.ids.update(parser.row.data['attrs']['uniqueids'])

        self.downloader()
        for parser in parsers:
            parser.process()
