'''
    XlPy/Spectra/parse
    __________________

    Links the proper spectral scans file with the parsing engine, and
    intializes the parsers.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import math
import operator as op
import weakref

from xldlib.onstart.main import APP
from xldlib.qt.objects import base
from xldlib.utils import logger
from xldlib.xlpy import wrappers

from . import link, mgf, mzml, mzxml


# PARSERS
# -------

PARSERS = {
    "mzxml": {
        "3.2.0, MSConvert": mzxml.ParseXml
    },
    "mzml": {
        '3.65.0, MSConvert': mzml.ParseXml
    },
    "mgf": {
        'None.None.None, MS Convert': mgf.ParseText,
        'None.None.None, PAVA': mgf.ParseText,
        'None.None.None, ProteoWizard': mgf.ParseText
    },
    "link": {
       "None.None.None, PAVA": link.ParseText
    }
}

# PARSER
# ------


@logger.init('scans', level='DEBUG')
class SpectralParser(base.BaseObject):
    '''
    Finds raw file type, and uses proper parser to extract
    peaklists and header information for MS searching.
    '''

    def __init__(self, row):
        super(SpectralParser, self).__init__()

        self.row = row
        self.source = weakref.proxy(self.app.discovererthread)

    @logger.call('scans', level='DEBUG')
    def __call__(self):
        '''On start, initiate parsers sequentially'''

        for key, group in self.row.spectra.items(ignore=self.row.spectra.ms1):
            fileobj = open(self.row.files[key], 'r')
            parser = self.getparser(fileobj, key, group)
            parser()

        self.setgradient()

    #     SETTERS

    def setgradient(self):
        '''Stores the runtime length information from the MS file'''

        precursor = next(self.row.spectra.values())

        # find max key is much faster due to dict interface than traversing
        # all the items
        num = max(precursor, key=int)
        runtime = precursor.getscan(num).getattr('retention_time')
        self.row.data['attrs']['runtime'] = int(math.ceil(runtime))

    #     GETTERS

    def getparser(self, fileobj, key, group):
        '''Finds the child Parser class and initiates an instance.'''

        engine = self.row.engines[key]
        cls = PARSERS[engine.name][engine.tostr()]
        return cls(fileobj, group, engine)


@wrappers.threadprogress(40, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Parsing raw spectra...")
def parsespectra():
    '''Calls the raw spectral parsing classes'''

    source = APP.discovererthread
    adjust = 1
    if source.quantitative:
        adjust = 2

    for index, row in enumerate(source.files):
        parser = SpectralParser(row)
        parser()

        progress = (40-20) * (index+1) / len(source.files)
        source.part_done.emit((20 + progress) / adjust)
