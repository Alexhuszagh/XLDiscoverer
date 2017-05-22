'''
    XlPy/MS1Quantitation/linking
    ____________________________

    Links the MS2 precursor scan to the MS1 scan, the scan for the
    original mass acquisition.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op
import weakref

from xldlib.definitions import ZIP
from xldlib.qt.objects import base
from xldlib.utils import logger
from xldlib.xlpy import scan_linkers, wrappers

# HELPERS
# -------


def setms1spreadsheet(spreadsheet, linkedscans):
    '''Sets the MS1 scan information to the spreadsheet'''

    scans = spreadsheet[(' ', 'Precursor Scan')]
    # (None, None) -> means precursor not found
    ms1scans, ms1rt = ZIP(*(linkedscans.get(i, (None, None)) for i in scans))
    spreadsheet[(' ', 'MS1 Scan')] = list(ms1scans)
    spreadsheet[(' ', 'MS1 RT')] = list(ms1rt)


# OBJECTS
# -------


@logger.init('quantitative', 'DEBUG')
class LinkMs1Scans(base.BaseObject):
    '''
    Links the MS1 transition lists to the MS2 scans for identified
    links.
    '''

    def __init__(self):
        super(LinkMs1Scans, self).__init__()

        self.source = weakref.proxy(self.app.discovererthread)

    @logger.call('linking', 'debug')
    def __call__(self):
        '''On call, links the MS2 scans to the MS1 scans'''

        self.set_linkers()
        for index, row in enumerate(self.source.files):
            self.setspreadsheetdata(index, row)
            self.setms1data(row)

    #    SETTERS

    def set_linkers(self):
        '''
        Presets all the scan linkers, which are required for precalculation
        if global searches are turned on.
        '''

        self.linkers = []
        for row in self.source.files:
            linker = scan_linkers.Ms1Linker(row)
            linker()
            self.linkers.append(linker)

    def setspreadsheetdata(self, index, row):
        '''Sets the MS1 scan data for each spreadsheet row'''

        linker = self.linkers[index]
        for spreadsheet in row.data['spreadsheet']['labeled']:
            setms1spreadsheet(spreadsheet, linker.linkedscans)

    def setms1data(self, row):
        '''Sets the MS1 data for each set of spreadsheet data'''

        for labels in row.transitions:
            index = labels.getattr('file')
            filerow = self.source.files[index]
            linker = self.linkers[index]

            spreadsheet = labels.getattr('spreadsheet')
            setms1spreadsheet(spreadsheet, linker.linkedscans)
            labels.setattr('spreadsheet', spreadsheet)


@logger.call('linking', 'debug')
@wrappers.runif(op.attrgetter('quantitative'))
@wrappers.threadprogress(120, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Linking MS1 scans...")
def linkms1():
    inst = LinkMs1Scans()
    inst()
