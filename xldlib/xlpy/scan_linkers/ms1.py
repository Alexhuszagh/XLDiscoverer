'''
    XlPy/Scan_Linkers/ms1
    _____________________

    Links the precursor ion scan for the cross-linked peptide
    to the MS1 acquisition scan.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger

# load objects/functions
from collections import defaultdict


# LINKER
# ------


@logger.init('linking', 'DEBUG')
class Ms1Linker(base.BaseObject):
    '''
    Creates list with precursor data for each MS2 scan, linking
    each MS2 scan to each MS1. Has no "validation" other than a max
    step interval since MS2 scans must have sequential MS2 children
    (not staggerred, IE, multi MS1 to MS2) and the same MS2 ion
    can be found in many MS1 scans (no ion selection).
    :
        >>> source.matched["precursor_num"][100]
        3075
        >>> source.matched["ms1_num"][66]
        3074
    '''

    def __init__(self, row):
        super(Ms1Linker, self).__init__()

        self.row = row
        self.group = row.spectra.getgroup('ms1')

        self.steps = defaults.DEFAULTS['ms1_scan_steps']
        self.error = False

        self.setscannums()

    @logger.raise_error
    def __call__(self):
        '''
        Finds the MS1 scan by probing the scan header with iterative
        steps to see if preceeding MS2 scans contain the prcursor MZ.
        '''

        self.setlinkedscans()
        self.setmatcheddata()

    #    SETTERS

    def setscannums(self):
        '''Sets the scan numbers and the vectorized arrays for each'''

        self.num = defaultdict(list)
        for index, num in enumerate(self.row.data['matched']["precursor_num"]):
            self.num[num].append(index)
        self.group.setscans()

    def setlinkedscans(self):
        '''Links each precursor scan to each MS1-level scan'''

        self.linkedscans = {}
        for num in self.num:
            ms1 = self.getms1scan(num)
            self.linkedscans[num] = ms1

    def setmatcheddata(self):
        '''Sets the MS1 scan data for the matched data'''

        self.row.data.setnull(keys=('ms1_num', 'ms1_rt'))
        for num, indexes in self.num.items():
            ms1num, ms1rt = self.linkedscans[num]
            for index in indexes:
                self.row.data['matched']['ms1_num'][index] = ms1num
                self.row.data['matched']['ms1_rt'][index] = ms1rt

    #    GETTERS

    def getms1scan(self, num):
        '''
        Iterative procedure to find precursor scan, and matches scan
        via presence of precursor.
        :
            index -- index in precursor list
            num -- product scan number
        '''

        for ms1num in self.group.findscan(num):
            ms1scan = self.group.getscan(str(ms1num))
            return tuple(ms1scan.getattrs(('num', 'retention_time')))

        self.error = True
        return None, None
