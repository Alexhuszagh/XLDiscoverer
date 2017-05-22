'''
    XlPy/MS1Quantitation/Extraction/hierarchical
    ____________________________________________

    Simple object to convert pre-parsed MS1 scans from hierarchical
    file formats to extracted ion chromatograms.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.qt.objects import base
from xldlib.utils import logger

from . import scans


# OBJECTS
# -------


@logger.init('quantitative', 'DEBUG')
class ProcessPreParsedScans(base.BaseObject):
    '''Converts peaklists to extract ion chromatograms'''

    def __init__(self, row, group):
        super(ProcessPreParsedScans, self).__init__()

        self.row = row
        self.group = group

        self.extractor = scans.ChromatogramExtractor(row)

    @logger.call('quantitative', 'debug')
    def __call__(self):
        '''On start'''

        keys = sorted(self.group, key=int)
        for key in keys:
            group = self.group.getscan(key)
            retentiontime = group.getattr('retention_time')
            self.extractor(retentiontime, group.mz[:], group.intensity[:])

        self.extractor.spectratotables()
        self.extractor.set_windows()
