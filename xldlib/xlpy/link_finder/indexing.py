'''
    XlPy/Link_Finder/indexing
    _________________________

    Generates a named tuple with the grouped indexes, the total indexes,
    and the filtered indexes for the link searching, to easily
    limit the search space and re-expand it.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from collections import namedtuple

from xldlib.definitions import ZIP
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger


# OBJECTS
# -------

Indexer = namedtuple("Indexer", "group filtered total")


@logger.init('xlpy', 'DEBUG')
class IndexerFactory(base.BaseObject):
    '''Creates namedtuple instances to sample all combinations easily'''

    def __init__(self, row, crosslinker):
        super(IndexerFactory, self).__init__()

        self.row = row

        source = self.app.discovererthread
        self.isobaric = source.parameters.isobaric[crosslinker.id]
        self.cluster = defaults.DEFAULTS['cluster_product_scans']

    def __call__(self, indexes):
        '''Returns a new indexer'''

        grouped = self.row.data.groupby(indexes=indexes)
        filtered = self.getfiltered(grouped)

        return Indexer(grouped, filtered, indexes)

    #     GETTERS

    def getfiltered(self, grouped):
        '''
        Processes indexes to selected for either clustered or non-clustered
        and drops the non-cross-linked peptides.
        '''

        # toggle switch: clusterMS3 scans or search globally
        if self.cluster:
            indexes = [i[0] for i in grouped.values()]
        else:
            indexes = [i for item in grouped.values() for i in item]
        # remove indexes without crosslinking fragments
        return sorted(self.getcontainscrosslinkers(indexes))

    def getcontainscrosslinkers(self, indexes):
        '''
        Drops indexes without the given cross-linker modifications,
        since they cannot form bridges. Considers isobaric cross-link
        modifications as well among selected cross-linkers.
        :
            indexes -- lists of indexes to values in data sublists

            {"name":"XL:A-Alkene", "formula":"C3 H2 O1",
            {"name":"XL:B-Alkene", "formula":"C3 H2 O1"}

        Both are isobaric and are therefore considered (for cocktail
        cross-linker assays, where multiple cross-linkers are used
        in one experiment.
        '''

        generator = self.row.data.getcolumn(indexes, 'modifications')
        for index, modification in ZIP(indexes, generator):
            if self.isobaric.containsfragments(modification):
                yield index
