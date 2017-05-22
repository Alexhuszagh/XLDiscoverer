'''
    XlPy/Link_Finder/scan
    _____________________

    Re-packable named sequence for to facilitate compacting data
    when searching particular index combinations from a precursor scan.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import itertools as it

from collections import namedtuple

from xldlib.definitions import ZIP
from xldlib.qt.objects import base
from xldlib.utils import logger, masstools

from . import crosslinks, indexing, maker, search


# OBJECTS
# -------


class Scan(namedtuple("Scan",
    "formula modifications start peptide "
    "z precursor_mz precursor_z indexer")):
    '''Subclass with facile repacking methods'''

    #    PUBLIC

    def repack(self, rows):
        '''Repacks the scan for smaller index combinations'''

        data = {}
        for column in MS3COLUMNS:
            data[column] = [getattr(self, column)[i] for i in rows]
        return self._replace(**data)

    def getppm(self, theoretical):
        return masstools.ppm(self.precursor_mz, self.precursor_z, theoretical)

    def getmz(self, currentcharge=0):
        return masstools.mz(self.precursor_mz, currentcharge, self.precursor_z)


# COLUMNS
# -------

MS3COLUMNS = (
    'formula',
    'modifications',
    'start',
    'peptide',
    'z'
)

MS2COLUMNS = (
    'precursor_mz',
    'precursor_z'
)

COLUMNS = MS3COLUMNS + MS2COLUMNS


# FACTORY
# -------


@logger.init('xlpy', 'DEBUG')
class ScanFactory(base.BaseObject):
    '''Scan object which can return a compacted copy based on local indexes'''

    def __init__(self, row, crosslinker):
        super(ScanFactory, self).__init__()

        self.row = row
        self.crosslinker = crosslinker

        ends = crosslinks.EndsFactory(row, crosslinker)
        self.combinations = crosslinks.CrossLinkerCombinations(ends)
        self.indexer = indexing.IndexerFactory(row, crosslinker)
        self._link = search.LinkFactory(row, crosslinker, ends)
        self._check = search.CheckLink()
        self._maker = maker.MakeLink(row, crosslinker)

    def __call__(self, indexes):
        '''Constructs a new scan item'''

        indexer = self.indexer(indexes)
        data = list(ZIP(*self.row.data.getcolumn(indexer.filtered, COLUMNS)))

        if data:
            # precursor data, only need one item, not list of items
            # no data in the case of non-compatible crosslinker
            for index in [-2, -1]:
                data[index] = data[index][0]

            return Scan(*data, indexer=indexer)

    #    ITERATORS

    def iterpeptide(self, scan):
        '''Sample all peptide combinations from the scan'''

        totalpeptides = len(scan.peptide)
        peptiderange = set(range(1, totalpeptides + 1))
        indexrange = range(totalpeptides)

        for peptidecount in peptiderange:
            # sample all combinations of each scan
            combinations = it.combinations(indexrange, peptidecount)
            for indexes in combinations:
                yield (scan.repack(indexes), indexes)

    def itercrosslinkers(self, scan, localindexes):
        '''Sample all crosslinker combinations from the scan'''

        for crosslinkernumber in self.combinations(scan):
            try:
                link = self._link(scan, crosslinkernumber)
            except:
                import pdb; pdb.set_trace()
            linkname = self._check(link)

            if linkname is not None:
                # crosslink successfully found
                yield self._maker(link, linkname, localindexes)
