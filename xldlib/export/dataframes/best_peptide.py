'''
    Export/Dataframes/best_peptide
    ______________________________

    Dataframe producer for the best_peptide report, or a standard
    report with links filtered for the best entries (either by file
    or globally).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import itertools as it
import operator as op

from collections import namedtuple
from functools import total_ordering

from xldlib.utils import logger, modtools

from . import base


# OBJECTS
# -------


@total_ordering
class CrosslinkScore(namedtuple("CrosslinkScore", "crosslink score")):
    '''Subclass with comparison operators'''

    def __eq__(self, other):
        return (other is not None) and (self.score == other.score)

    def __gt__(self, other):
        return (other is None) or (self.score > other.score)

    def __lt__(self, other):
        return not self > other

    def __ge__(self, other):
        return (other is None) or (self.score >= other.score)

    def __le__(self, other):
        return not self >= other


class BestCrosslink(namedtuple("BestCrosslink", "linkage file")):
    '''Subclass with default arguments'''

    def __new__(cls, linkage, file=None):
        return super(BestCrosslink, cls).__new__(cls, linkage, file)


@logger.init('spreadsheet', level='DEBUG')
class Dataframe(base.MatchedDataframe):
    '''
    Best Peptide dataframe creator, an independent report (does not
    depend on data from other reports).
    '''

    def __init__(self, *args, **kwds):
        self.infile = kwds.pop('infile', False)
        super(Dataframe, self).__init__(*args, **kwds)

        self.seen = set()

    @logger.call('report', level='DEBUG')
    def __call__(self, crosslinks, linkages):
        '''Adds the crosslinks to the current dataframe on call'''

        self.set_dimensions(crosslinks)
        self.set_named_columns(self.columns.getordered(self.dimensions))

        crosslinks = self.getbestcrosslinks(crosslinks)
        self.set_version()
        self.set_subdataframes()

        for crosslink in crosslinks:
            linkage = linkages[(crosslink.row, crosslink.index)]
            self._append(crosslink, linkage)

        # conatenate subdataframes to the main holder
        self._sort()
        self._concat()
        self._rename(self.dimensions)

    #     GETTERS

    def getbestcrosslinks(self, crosslinks):
        '''Returns the best identification among the crosslinks'''

        crosslinks = sorted(crosslinks, key=op.attrgetter('row'))
        grouped = it.groupby(crosslinks, key=op.attrgetter('row'))

        best = {}
        for row, crosslinks in grouped:
            scorer = modtools.ScoreCrossLinks(self.matched[row])
            for crosslink in crosslinks:

                # add only if the new value is better than the previous entry
                key = self.__getkey(crosslink)
                value = self.__getvalue(scorer, crosslink)
                best[key] = max(value, best.get(key))

        # return our filtered entries
        return [i.crosslink for i in best.values()]

    def __getkey(self, crosslink):
        '''Returns a unique key for each linkage'''

        if self.infile:
            return BestCrosslink(crosslink.crosslink.frozen, crosslink.row)
        else:
            return BestCrosslink(crosslink.crosslink.frozen)

    def __getvalue(self, scorer, crosslink):
        '''Returns a namedtuple with the score for each item'''

        return CrosslinkScore(crosslink, scorer(crosslink.crosslink))
