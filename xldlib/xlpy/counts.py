'''
    XlPy/counts
    ___________

    Stores the link counts and provides methods for adding counts.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import copy

from xldlib.resources.parameters import reports
from xldlib.utils import logger

# load objects/functions
from collections import OrderedDict


# TEMPLATE
# --------

TEMPLATE = [
    ('Standard', OrderedDict([
        ('interlink', set()),
        ('intralink', set()),
        ('deadend', set())
    ])),
    ('Low Confidence', OrderedDict([
        ('interlink', set()),
        ('intralink', set()),
        ('deadend', set())
    ])),
    ('Fingerprint', OrderedDict([
        ('interlink', set())
    ])),
    ('Incomplete', OrderedDict([
        ('multilink', set()),
        ('single', set()),
    ])),
]


@logger.init('crosslinking', 'DEBUG')
class TotalCounts(OrderedDict):
    '''Definitions for counts'''

    def __init__(self):
        super(TotalCounts, self).__init__(copy.deepcopy(TEMPLATE))

    def add(self, items):
        '''Adds counts to self.totals from a linkname/linktype pair'''

        crosslinks = (i.crosslink for i in items)
        for crosslink in crosslinks:
            linkname = reports.LINKNAMES(crosslink.name)
            linktype = reports.LINKTYPES(crosslink.type)
            self[linkname][linktype].add(crosslink.frozen)

