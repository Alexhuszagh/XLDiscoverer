'''
    XlPy/Link_Finder/crosslinks
    ___________________________

    Calculates the theoretical crosslinker combinations from a given
    fragment composition and peptide count.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import math

from collections import Counter, namedtuple

from xldlib.definitions import ZIP
from xldlib.general import sequence
from xldlib.qt.objects import base
from xldlib.utils import logger, modtools



# OBJECTS
# -------


@sequence.serializable("CrosslinkModifiedEnds")
class Ends(namedtuple("Ends", "link dead number")):
    '''Subclass with proper loading/uncloading modes'''

    @property
    def isdeadend(self):
        return sum(self.link.values()) == self.number


# CROSSLINKER ENDS
# ----------------


@logger.init('xlpy', 'DEBUG')
class EndsFactory(base.BaseObject):
    '''Class factory for ends tuples'''

    def __init__(self, row, crosslinker):
        super(EndsFactory, self).__init__()

        source = self.app.discovererthread
        self.isobaric = source.parameters.isobaric[crosslinker.id]

        self.reactivecounter = Counter(crosslinker.ends.aminoacid)
        self.residuefinder = modtools.ResidueFinder(row, crosslinker)

    def __call__(self, scan, crosslinknumber):
        '''
        Calculates the number dead-end and bridge types and instantiates
        a namedtuple instance
        '''

        linkends = self.getlinkmodified(scan)
        maxends = self.maxlinkends(crosslinknumber)
        deadends = self.getdeadends(linkends, maxends)

        return Ends(linkends, deadends, crosslinknumber)

    #     GETTERS

    def getlinkmodified(self, scan):
        '''
        Grabs the number of link-modified ends for a given peptide
        combination and cross-linker count. Indexes these mods locally
        to the peptide.
        '''

        residues = []
        for peptide, modification in ZIP(scan.peptide, scan.modifications):

            crosslinker_positions = self.getpositions(modification)
            for position in crosslinker_positions:
                residue = self.residuefinder(peptide, position)
                residues.append(residue)

        return Counter(residues)

    def maxlinkends(self, crosslink_number):
        '''
        Calculates the maximum number of cross-linker link-ends for
        each possible conjugated residue.
        '''

        ends = {}
        for res, count in self.reactivecounter.items():
            ends[res] = count * crosslink_number
        return ends

    @staticmethod
    def getdeadends(link_ends, max_links):
        '''
        Calculates number of dead-ends simply by subtracting
        the number of link-ends from the total ends.
        :
            link_ends -- dict with crosslink ends modifying residues
            max_links -- dict with total crosslinker ends per residue
        '''

        for residue_csv in max_links:
            residue_set = set(residue_csv.split(','))
            for res, count in link_ends.items():
                if res in residue_set:
                    max_links[residue_csv] -= count

        return max_links

    def getpositions(self, modification):
        '''Returns the crosslinker fragment positions on the peptide'''

        modification = modification.unpack()
        for name, positions in modification.items():
            if name in self.isobaric:
                for position in positions:
                    yield position



@logger.init('xlpy', 'DEBUG')
class CrossLinkerCombinations(base.BaseObject):
    '''
    Calculates range of theoretical cross-link numbers from a given
    scan with a give number of fragments. First, calculates the
    crosslink fragment count and peptide count, and then sets the bounds
    on the crosslinker number.
    '''

    def __init__(self, ends):
        super(CrossLinkerCombinations, self).__init__()

        self.ends = ends
        self.reactivecounter = ends.reactivecounter

    def __call__(self, scan):
        '''Generates a set to iterate over all combinations'''

        link_ends = self.ends.getlinkmodified(scan)
        peptides = len(scan.peptide)

        lower = self.getminimum(peptides, link_ends)
        upper = self.getmaximum(peptides, link_ends)

        return {i for i in range(lower, upper + 1)}

    #     GETTERS

    def getminimum(self, peptides, link_ends):
        '''Grabs the maximum of the min required and possible crosslinkers'''

        return max(
            self.getminimumrequired(peptides),
            max(self.getminimumpossible(link_ends))
        )

    def getminimumrequired(self, peptides):
        '''
        Calculates the number of cross-linkers required
        to bridge k peptides, which is simply ceil((k-1)/(r-1)),
        where r is the number of reactive sites and k is the number
        of peptides.
        This calculates the minimum without any knowledge on the modified
        residues, and so provides a good but incomprehensive base
        filter for heteropolyfunctional crosslinkers.
        '''

        # calculate upper bound on crosslink count
        if peptides > 1:
            count = (peptides - 1) / (sum(self.reactivecounter.values()) - 1)
            return int(math.ceil(count))
        else:
            return 1

    def getminimumpossible(self, link_ends):
        '''
        Calculates the minimum number of cross-linkers required
        as determined by the fragment counts. This exploits the reactive
        site counts and the fragment counts to determine the minimum
        number of crosslinker modifications possible.
        '''

        yield 0
        for residue, reactivity_count in self.reactivecounter.items():
            yield int(math.ceil(link_ends[residue] / reactivity_count))

    def getmaximum(self, peptides, link_ends):
        '''
        Calculates the maximum number of cross-linkers possible
        given a peptide combination with a given number of cross-linker
        fragments.
        The number of link_ends is just the number of peptides + the
        minimum number of cross-linkers -1 (each peptide needs 1 end,
        plus one for each extra cross-linker required after the first
        (since the first bridges as many peptides as reactive sites,
        and each subsequent bridges the reactive sites -1), or:
        k = number of peptides
        link_ends = min+k-1

        The max is just the minimum of cross-linkers + the number of
        fragments - the number of fragments occupied by link ends in
        this minimum, or:
        f = fragments
        max = min+f-link_ends

        By combining the two, we get the elegant:
        max = fragments+1-peptides
        '''

        return sum(link_ends.values()) + 1 - peptides
