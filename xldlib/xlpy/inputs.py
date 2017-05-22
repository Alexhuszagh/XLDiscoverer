'''
    XlPy/inputs
    ___________

    Validates input file selection, configurations, and matches file types.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op

from xldlib.onstart.main import APP
from xldlib.utils import logger
from xldlib.xlpy import wrappers


# CHECKER
# -------


@logger.call('xlpy', 'debug')
@wrappers.threadprogress(3, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Checking inputs...")
def checkinputs():
    '''Validates the processed input files'''

    source = APP.discovererthread

    # crosslinkers
    source.parameters.checkcrosslinkers()

    # files
    source.files.checkfile()
    source.files.unzipfiles()
    source.files.matchfile()
    if source.quantitative:
        source.files.checkengine()
