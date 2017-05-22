'''
    XlPy/Link_Finder/sorting
    ________________________

    Sorts the link indexes based on the sequenced protein names,
    the crosslinker fragment positions, and the modification positions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.definitions import ZIP
from xldlib.qt.objects import base
from xldlib.utils import logger


# SORTER
# ------


@logger.init('xlpy', 'DEBUG')
class SortLinkPeptides(base.BaseObject):
    '''
    Sorts the peptides within each given link to ensure consisten link
    reporting and ordering.
    '''

    def __init__(self, row, crosslinker):
        super(SortLinkPeptides, self).__init__()

        self.row = row
        self.crosslinker = crosslinker

        source = self.app.discovererthread
        self.isobaric = source.parameters.isobaric[crosslinker.id]
        self.engine = row.engines['matched']

        self.setmincrosslinkpositions()

    @logger.call('xlpy', 'debug')
    def __call__(self, crosslink):
        '''Sorts the given link'''

        sortkey = self.getsortkey(crosslink.index)
        crosslink.index.sort(key=sortkey.get)

    #    GETTERS

    def getsortkey(self, rows):
        '''Returns a sortable key for the link rows'''

        names = self.row.data.getcolumn(rows, 'preferred')
        positions = (self.mincrosslinkpositions[i] for i in rows)

        return {i: (n, p) for i, n, p in ZIP(rows, names, positions)}

    def getcrosslinkerpositions(self, modification):
        '''Grabs all crosslinker mod positions from a given mod dictionary.'''

        certain = modification['certain']
        for position in self.getmodpositions(certain):
            yield position

        uncertain = modification['uncertain']
        for modificationdict in uncertain:
            for position in self.getmodpositions(modificationdict):
                yield position

    def getmodpositions(self, modification):
        '''
        Grabs all mod positions within a mod dict with names with the
        mod_names list.
        '''

        for name, positions in modification.items():
            if name in self.isobaric:
                for position in positions:
                    yield self.engine.key(position)

    #    SETTERS

    def setmincrosslinkpositions(self):
        '''
        Grabs the minimum position for a series of cross-linkers
        from a given mod set. Returns a list for each mod within the
        mod_list.
        '''

        self.mincrosslinkpositions = []

        for row in self.row.data.iterrows(('modifications', 'start'), True):
            positions = self.getcrosslinkerpositions(row['modifications'])
            try:
                minposition = min(positions)
                self.mincrosslinkpositions.append(minposition + row['start'])
            except ValueError:
                # argument is a null sequence, multiple crosslinkers
                self.mincrosslinkpositions.append(float("nan"))
