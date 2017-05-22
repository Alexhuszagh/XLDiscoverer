'''
    XlPy/Link_Finder/core
    _____________________

    Core link searching utility, which sorts each file in a threaded
    manner to allow concurrent link detection.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op

from xldlib.onstart.main import APP
from xldlib.qt.objects import base
from xldlib.resources.parameters import reports
from xldlib.utils import logger
from xldlib.xlpy import wrappers

from . import expand, scan, sorting

# DATA
# ----

BEST_LINKAMES = (
    'Standard',
    'Low Confidence',
    'Fingerprint',
    'Incomplete'
)


# HELPERS
# -------


def getbestlinkname(unfiltered):
    '''
    Extracts and grabs the best linkname (standard->lowconf->multi)
    for a given set of links from a given MS2 parent.
    '''

    # iteratively check to see the linknames
    for name in BEST_LINKAMES:
        linkname = reports.LINKNAMES[name]
        filtered = [i for i in unfiltered if i.name == linkname]
        if filtered:
            return filtered
    # subsequent arguments expect a sequence
    return []


# SEARCHER
# --------


@logger.init('xlpy', 'DEBUG')
class SearchLinks(base.BaseObject):
    '''
    Returns dictionary (self.links) with matched data as a list
    with link namedtuples as values.
    :
        Link(index=(100, 101), name="Standard", type="interlink",
        ppm=-0.532, ppm_set=set(), ends=(Ends(link={'K':2},
        dead={'K':0}, num=1)))
    '''

    def __init__(self, row, crosslinker):
        super(SearchLinks, self).__init__()

        self.row = row
        self.crosslinker = crosslinker

        self.sorter = sorting.SortLinkPeptides(row, crosslinker)
        self.scans = scan.ScanFactory(row, crosslinker)
        self.expander = expand.LinkExpander(row, crosslinker)
        # self.pmfbase = PMFBase(row, xlkey, self)

        source = self.app.discovererthread
        self.fingerprinting = source.fingerprinting

    @logger.raise_error
    def __call__(self):
        '''
        Iterate sequentially over scans to mathematically exhaust
        all possible link combinations.
        '''

        for indexes in self.row.linked.index.values():
            scan = self.scans(indexes)
            if scan:
                crosslinks = self.getcrosslinks(scan)
                crosslinks = self.expander(crosslinks, scan)

                for crosslink in crosslinks:
                    self.sorter(crosslink)
                    self.row.data['crosslinks'].append(crosslink)

    #    GETTERS

    def getcrosslinks(self, base_scan):
        '''
        Finds any possible cross-link by iterating over the number
        of peptides, then the maximum number of
        cross-linkers for the peptide number. Returns links
        with indexes as local values.
        :
            scan -- instance of ScanTuple from link_finder.scan
        '''

        crosslinks = []
        for scan, indexes in self.scans.iterpeptide(base_scan):
            crosslinks.extend(self.scans.itercrosslinkers(scan, indexes))

        # check missing only after exhausting search, due to high "cost"
        # and the redundancy since the crosslink number is recalculated
        # with each iteration
        if not crosslinks and self.fingerprinting:
            # then need to try single matching, peptide_count = 1
            # TODO: broken
            import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()
            self.pmfbase.search_singles(crosslinks, scan, index)

        return getbestlinkname(crosslinks)


# SEARCH HANDLER
# --------------


@logger.call('xlpy', 'debug')
@wrappers.threadprogress(50, 2, op.attrgetter('quantitative'))
@wrappers.threadmessage("Searching for crosslinks...")
def calculatelinks():
    '''
    Searches all link permutations after first grouping by MS3 scan
    with identical crosslinker profile,
    '''

    source = APP.discovererthread

    for row in source.files:
        for crosslinker in source.parameters.crosslinkers.values():
            searcher = SearchLinks(row, crosslinker)
            searcher()
