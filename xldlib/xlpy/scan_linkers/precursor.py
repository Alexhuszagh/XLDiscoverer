'''
    XlPy/Scan_Linkers/precursor
    ___________________________

    Links all the product scans to their precursors using
    Scan_Linkers.precursor_product.ScanLinker

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import operator as op
import weakref

from xldlib import exception
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger
from xldlib.xlpy import wrappers


# SCAN LINKER
# -----------


@logger.init('linking', 'DEBUG')
class ScanLinker(base.BaseObject):
    '''
    Creates list with precursor data for each scan, linking
    product scan to precursor scan for each matched peptide. Enables
    pairing of scans for MS1 mass fingerprinting.

    Ex.
        >>> source.matched["num"][100]
        3078
        >>> source.matched["num"][66]
        3079
        >>> source.matched["precursor_num"][100]
        3075
        >>> source.matched["precursor_num"][66]
        3075
    '''

    def __init__(self, row):
        super(ScanLinker, self).__init__()

        self.row = row
        self.noprecursor = []

        self.precursor = weakref.proxy(self.row.linked.precursor)

    @logger.call('linking', 'debug')
    def __call__(self):
        '''
        Finds the precursor scan info, which is required for MS1 mass
        matching. Reports the listed precursor scan number if possible.
            Ex.
                MGF PAVA:
                    ...
                    MS2_SCAN_NUMBER = 3075
                    ...
                mzXML:
                    ...
                    <precursorMz precursorScanNum="50"
                    ....
        If the precursor number is not in scan header, iterative scans
        are sampled to see if preceeding MS2 scans contain the precursor
        m/z.
        '''

        self.row.linked.delevel()
        for num in self.row.data['matched']['num']:
            self.row.linked(num)

        self.row.data.setnull()
        self.setlinkeddata()

    #     SETTERS

    def setlinkeddata(self):
        '''
        Links the identified IDs precursor to product, with the possibility,
        with the possibility of linking a single product scan to multiple
        precursor scans if the parent ion from the product scan is found
        in all those precursor scans and checkprecursor is on.
        '''

        # use a copy to avoid infinite iterationwith row duplication
        nums = self.row.data['matched']['num'][:]
        for index, num in enumerate(nums):
            precursors = self.row.linked.prod.get(num, [])

            for idx, precursor_num in enumerate(precursors):
                precursor = self.precursor.get(str(precursor_num))
                if idx == 0 and precursor is not None:
                    self.row.data.setfromdict(precursor.todict(), index)
                elif precursor is not None:
                    self.duplicaterow(precursor, index)
                elif idx == 0:
                    self.noprecursor.append(index)

            if not precursors:
                self.noprecursor.append(index)

    def duplicaterow(self, precursor, index):
        '''Duplicates a row, then relinks that new row to another precursor'''

        row = self.row.data.getrow(index, asdict=True)
        self.row.data.setfromdict(row)
        self.row.data.setfromdict(precursor.todict(), index)


# LINKER
# ------


@logger.init('linking', 'DEBUG')
class LinkPrecursorScans(base.BaseObject):
    '''
    Links precursor to product scans (MS3->MS2) and groups them for fast
    link identification and processing
    '''

    def __init__(self):
        super(LinkPrecursorScans, self).__init__()

        self.source = weakref.proxy(self.app.discovererthread)
        self.removed = [False] * len(self.source.files)
        self.noprecursor = []

        self.checkprecursor = defaults.DEFAULTS['check_precursor']
        self.maxmissing = defaults.DEFAULTS['missing_precursor_threshold']
        self.scanthreshold = float("inf")
        if self.checkprecursor:
            self.scanthreshold = self.maxmissing

    @logger.call('linking', 'debug')
    def __call__(self):
        '''On start'''

        for row in self.source.files:
            linker = ScanLinker(row)
            linker()
            self.noprecursor.append(linker.noprecursor)

        # Remove partially processed or empty data
        self.removeempty()
        self.removeunmatched()
        self.removemissing()

        for row in self.source.files:
            row.linked.group()

    #     REMOVERS

    @wrappers.ignore('015')
    def removeempty(self):
        '''
        Checks the matched scans to determine if any have no matched
        peptides after decoy dropping and cross-linker filtering.
        '''

        for row in self.source.files:
            if len(row.data['matched']['id']) == 0:
                self.removed[row.index] = True
                yield row.index

    @wrappers.ignore('003')
    def removeunmatched(self):
        '''
        Checks the matched scans to determine if any have high levels
        of missing precursors, based on the thread.noprecursor
        / len(total data). If so, deletes those entries, warns the user
        and continue the analysis
        '''

        for index, row in enumerate(self.source.files):
            if self.abovethreshold(index, row):
                if row.index not in row.parent().ignored:
                    self.removed[row.index] = True
                    yield row.index

    def removemissing(self):
        '''
        Checks the matched scans to determine if any have low levels
        of missing precursors, based on the thread.noprecursor
        / len(total data). If so, deletes the matched scans associated
        with those entires.
        '''

        for index, row in enumerate(self.source.files):
            if self.belowthreshold(index, row) and not self.removed[row.index]:
                # get the scan numbers
                noprecursor = set(self.noprecursor[row.index])
                missing = sorted(noprecursor, reverse=True)
                num = list(row.data.getcolumn(missing, 'num'))
                row.data.deleterows(missing)

                # emit the missing precursors
                search = row.data['attrs']['search']
                msg = exception.CODES['011'].format(search)
                self.source.helper.emitsequence(msg, num, "green")

    #     CHECKERS

    def abovethreshold(self, index, row):
        '''
        Function to determine if a thread's unmatched precursors
        is above the acceptable threshold.
        '''

        missing = len(self.noprecursor[index])
        scanlength = len(row.data['matched']['id'])
        if not self.checkprecursor:
            # if the scans don't line up and no precursor checking,
            # only return an error if a reported error or greater than 0.2
            return missing > (scanlength * 0.2)
        else:
            return (missing * 100 / scanlength) > self.maxmissing

    def belowthreshold(self, index, row):
        '''
        Function to determine if a thread's unmatched precursors
        is below the acceptable threshold, but still existant.
        '''

        length = len(row.data['matched']['id'])
        if not length:
            return False

        percent_missing = len(self.noprecursor[index]) / length
        return 0 < percent_missing < self.scanthreshold


@logger.call('linking', 'debug')
@wrappers.threadprogress(45, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Linking precursor scans...")
def linkprecursor():
    inst = LinkPrecursorScans()
    inst()
