'''
    XlPy/MS1Quantitation/Extraction/core
    ____________________________________

    Core module to extract and process MS1 scans to extracted ion
    chromatograms, or XICs.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op

from xldlib.onstart.main import APP
from xldlib.utils import logger
from xldlib.xlpy import wrappers
from xldlib.xlpy.spectra import pava

from . import hierarchical


# PARSERS
# -------

PARSERS = {
    "mgf": {
        'None.None.None, Pava FullMs': pava.ParseFullms
    }
}


# OBJECTS
# -------


def parsems1():
    '''Parses the MS1 scans file and simultaneously extracts the MS1 scans'''

    source = APP.discovererthread
    for row in source.files:
        group = row.spectra.getgroup('ms1')
        fileobj = open(row.files['ms1'], 'r')

        engine = row.engines['ms1']
        cls = PARSERS[engine.name][engine.tostr()]
        parser = cls(row, group, fileobj)
        parser()


def extractscans():
    '''Extracts ion chromatograms from the pre-processed MS1 file'''

    source = APP.discovererthread
    for row in source.files:
        group = row.spectra.getgroup('ms1')
        processor = hierarchical.ProcessPreParsedScans(row, group)
        processor()


@logger.call('quantitative', 'debug')
@wrappers.runif(op.attrgetter('quantitative'))
@wrappers.threadprogress(80, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Extracting MS1 scans...")
def extractms1():
    '''Handler which creates and processes the MS1 extraction for all rows'''

    source = APP.discovererthread
    source.transitions.init_cache()

    if source.files.ishierarchical():
        extractscans()
    else:
        parsems1()
