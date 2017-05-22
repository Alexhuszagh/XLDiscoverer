'''
    XlPy/MS1Quantitation/Isotope_Labels/matching
    ____________________________________________

    Tools to correlate theoretical modifiction profiles to
    actual ones.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# laod modules
import copy

from xldlib.qt.objects import base
from xldlib.utils import logger

# load objects/functions
from collections import defaultdict, namedtuple


# TEMPLATES
# ---------

EXPERIMENTAL_TEMPLATE = {
    'standard': defaultdict(list),
    'crosslinker': defaultdict(list),
    'counts': {}
}


# OBJECTS
# -------


class Experimental(namedtuple("Experimental", "standard crosslinker counts")):
    '''Definitions for experimental modification counts'''

    def __new__(cls, **kwds):
        for key, value in EXPERIMENTAL_TEMPLATE.items():
            kwds.setdefault(key, copy.deepcopy(value))
        return super(Experimental, cls).__new__(cls, **kwds)


# MODIFICATION COUNTER
# --------------------


@logger.init('quantitative', 'DEBUG')
class ModificationCounter(base.BaseObject):
    '''
    Calculates the actual isotope-labelled modifications (as specified
    in the isotope labeling profile).
    '''

    def __init__(self):
        super(ModificationCounter, self).__init__()

        source = self.app.discovererthread
        self.fragments = source.parameters.fragments
        self.profile = source.parameters.profile

        self.setisotopelabels()

    def __call__(self, rowdata):
        '''
        Returns the modification counts associated isotope labels,
        and separates the remaining standard and crosslinking modifications.
        '''

        experimental = Experimental()

        for name, positions in rowdata['modifications'].unpack().items():
            if name in self.isotopelabels:
                experimental.counts[name] = len(positions)
            elif name in self.fragments:
                experimental.crosslinker[name] += positions
            else:
                experimental.standard[name] += positions
        return experimental

    #     SETTERS

    def setisotopelabels(self):
        '''Generates a hashtable comprising all the isotope labels'''

        self.isotopelabels = set()
        for values in self.profile.getlabels().values():
            self.isotopelabels.update(i.name for i in values)

# OBJECTS
# -------

Theoretical = namedtuple("Theoretical", "positions counts")


# THEORETICAL PROFILES
# --------------------


@logger.init('quantitative', 'DEBUG')
class TheoreticalModifications(base.BaseObject):
    '''
    Calculates the theoretical modifications for various different
    parameters, considering on isotope labels.
    '''

    def __init__(self, row):
        super(TheoreticalModifications, self).__init__()

        self.row = row
        self.engine = row.engines['matched']

        source = self.app.discovererthread
        self.profile = source.parameters.profile
        self.isotopelabels = self.profile.getlabels()

    def __call__(self, rowdata):
        '''Returns the theoretical modification counts for '''

        for index in range(len(self.profile.populations)):
            yield self.getpopulation(index, rowdata)

    #     GETTERS

    def getpopulation(self, index, rowdata):
        '''
        Returns the theoretical isotope-label counts for that
        isotope-labeled population from matched query data.
        '''

        positions = defaultdict(list)
        counts = defaultdict(int)

        modifications = self.isotopelabels[index]
        for modification in modifications:
            position = self.getcounts(modification, rowdata)
            if position:
                # add the positions and counts only if present, so
                # it allows direct == comparisons to experimental
                positions[modification.name] += position
                counts[modification.name] += len(position)

        return Theoretical(positions, counts)

    def getcounts(self, modification, rowdata):
        '''
        Returns the number of instances of the modification within
        the target peptide.
        '''

        if modification.protein_nterm and rowdata['start'] == 1:
            return self._getproteinnterm(modification, rowdata['peptide'])

        elif modification.protein_cterm:
            return self._getproteincterm(modification, rowdata['peptide'])

        elif modification.nterm:
            return self._getnterm(modification, rowdata['peptide'])

        elif modification.cterm:
            return self._getcterm(modification, rowdata['peptide'])

        else:
            return list(modification.getinternalindex(rowdata['peptide']))

    # POSITION GETTERS

    def _getproteinnterm(self, modification, peptide):
        if modification.gettermindex(peptide, 0):
            return [self.engine.defaults.nterm]

    @staticmethod
    def _getproteincterm(modification, peptide):
        raise NotImplementedError

    def _getnterm(self, modification, peptide):
        if modification.gettermindex(peptide, 0):
            return [self.engine.defaults.nterm]

    def _getcterm(self, modification, peptide):
        if modification.gettermindex(peptide, -1):
            return [self.engine.defaults.cterm]
