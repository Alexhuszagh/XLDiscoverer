'''
    Export/Spreadsheet/core
    _______________________

    Core writer to generate spreadsheet data from Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import operator as op

from xldlib.onstart.main import APP
from xldlib.utils import logger
from xldlib.xlpy import wrappers

from . import crosslinks, single


# SPREADSHEET
# -----------


@logger.call('spreadsheet', 'debug')
@wrappers.threadprogress(55, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Processing spreadsheet data...")
def createspreadsheets():
    '''Generates the spreadsheet data for dataframe creation'''

    source = APP.discovererthread

    for row in source.files:
        crosslinkdata = crosslinks.CreateCrosslinkData(row)
        singledata = single.CreateSingleData(row)

        for index, crosslink in enumerate(row.data['crosslinks']):
            rowdata = crosslinkdata(crosslink)
            row.data['spreadsheet']['crosslinks'].append(rowdata)

        singledata()
