'''
    XlPy/Link_Finder/expand
    _______________________

    Expands the clustered MS3 scans to the matched link types for
    MS3 peptides with different IDs but the same parent mass.

    Clustering is used to reduce the search space.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import itertools as it

from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger, modtools
from xldlib.xlpy.tools import frozen

# LINK EXPANSION
# --------------


@logger.init('crosslinking', 'DEBUG')
class LinkExpander(base.BaseObject):
    '''
    Expands redundant IDs to produce all possible combinations.
    Can be desirable for sequences with a few repetitive sequence
    matches, but undesirable for highly repetitive sequences
    or highly homologous proteins (IE, histones, heat-shock, etc.).
    It also filters out redundant IDs.
    '''

    def __init__(self, row, crosslinker):
        super(LinkExpander, self).__init__()

        self.row = row
        self.crosslinker = crosslinker

        source = self.app.discovererthread
        self.isobaric = source.parameters.isobaric[crosslinker.id]
        self.sorter = modtools.SortLinks(row)
        self.freezer = frozen.CrosslinkFreezer(row, crosslinker)

        self.setmaxexpanded()

    def __call__(self, crosslinks, indexer):
        '''Expands the links within the link set'''

        if not defaults.DEFAULTS['cluster_product_scans']:
            return crosslinks
        else:
            return self.getexpanded(crosslinks, indexer)

    #     SETTERS

    def setmaxexpanded(self):
        '''Returns the max number of possible IDs reported for an MS2 scan'''

        expansion = defaults.DEFAULTS['expand_ambiguous']
        if expansion == "None":
            self.maxexpanded = 1
        elif expansion == "Interesting":
            self.maxexpanded = defaults.DEFAULTS['interesting_ambiguous']
        else:
            self.maxexpanded = -1

    #     GETTERS

    def getexpanded(self, crosslinks, scan):
        '''
        Expands the crosslinks to all ambiguous identifications (those
        with the same score from the same ID)
        '''

        self.sorter(crosslinks)
        frozencrosslinks = set()

        for crosslink in crosslinks:
            generator = self.getcombinations(crosslink, scan)
            for indexes in generator:
                # need to sort only for unique ids
                frozen = self.freezer(indexes, crosslink.ends)
                if frozen not in frozencrosslinks:
                    frozencrosslinks.add(frozen)
                    yield crosslink._replace(index=indexes, frozen=frozen)

                    if len(frozencrosslinks) == self.maxexpanded:
                        # break look when max redundancy found
                        break

    def getcombinations(self, crosslink, scan):
        '''
        Expands using itertools.product to every combination from
        a given MS3 scans.
        '''

        num = list(self.row.data.getcolumn(crosslink.index, 'num'))
        # grab all redundant IDs that map to the same ms3
        # fingerprint event, no MS3 score or scan so just return it
        if any(isinstance(i, float) for i in num):
            # nan or inf in the scans
            grouped = [[i] for i in crosslink.index]
        else:
            grouped = [scan.indexer.group[i] for i in num]

        # filter only for those with the same number of xl fragments
        indexes = self.getisocrosslinker(grouped, crosslink.index)
        return (list(i) for i in it.product(*indexes))

    def getisocrosslinker(self, grouped, linkindexes):
        '''
        Filters indexes for those that contain crosslinker
        fragments. Returns as a list within a list, as before.
        Also asserts that the cross-linker fragment number is
        identical to the pre-expanded form.

            >>> indexes
            [[8558, 8780], [7310]]
            >>> baseIndexes
            [8558, 7310]
        '''

        for idx, indexes in enumerate(grouped):
            baseindex = linkindexes[idx]
            samescan = list(self.getsamescan(baseindex, indexes))
            if samescan:
                yield samescan

    def getsamescan(self, baseindex, indexes):
        '''
        Returns the matched peptides the come from the same product scan
        only if they have the same number of crosslinker modifications
        as the matched identification.
        :
            idx -- current index inside the grouped indexes
            linkindexes -- indexes for the identified link
            indexes -- grouped indexes, to expand
        '''

        basecrosslinknumber = sum(self.getcrosslinkcount(baseindex))
        for index in indexes:
            crosslinknumber = sum(self.getcrosslinkcount(index))

            # only if identical number, otherwise different bridging mode
            if basecrosslinknumber == crosslinknumber:
                yield index

    def getcrosslinkcount(self, index):
        '''
        Returns the number of cross-linker fragments in a given mod
        set. Assumes the uncertain mods are identical in composition
        and differ solely in the position of the mods.
        '''

        mod = self.row.data['matched']['modifications'][index].unpack()

        yield 0
        for name, positions in mod.items():
            if name in self.isobaric:
                yield len(positions)
