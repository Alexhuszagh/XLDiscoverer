'''
    XlPy/MS1Quantitation/Isotope_Labels/labeler
    ___________________________________________

    Creates all permutations of isotope-labeled crosslinks from fully-
    labeled or unlabeled sequenced crosslinks.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import itertools as it
import types

from collections import defaultdict, namedtuple

from xldlib.definitions import ZIP
from xldlib.general import sequence
from xldlib.objects import matched
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger, masstools
from xldlib.xlpy.tools import frozen


# PERMUTATIONS
# ------------


@logger.init('quantitative', 'DEBUG')
class CalculateIsotopePermutations(base.BaseObject):
    '''
    Call method returns an iterator with all the isotope profile permutations
    from the given isotope label.
        Crosslink(index=[0, 1]), isotopestates = (1, 1)
            -> ((0, 0), (0, 1), (1, 0), (1, 1))
    '''

    def __init__(self):
        super(CalculateIsotopePermutations, self).__init__()

        profile = self.app.discovererthread.parameters.profile
        self.isotopestates = range(len(profile.populations))

    def __call__(self, isotopestates):
        '''
        Returns an iterator with each permutation of the isotope states.
        If the isotope states do not match and there is no isotope mixing,
        returns a NoneType.
        '''

        isotopestates = self._isotopechecker(isotopestates)
        if defaults.DEFAULTS['include_mixed_populations']:
            return self.__withmixing(isotopestates)

        else:
            return self.__nomixing(isotopestates)

    #    CALCULATIONS

    def __withmixing(self, isotopestates):
        '''Returns the cartesian product of the profile isotope states'''

        return it.product(self.isotopestates, repeat=len(isotopestates))

    def __nomixing(self, isotopestates):
        '''
        Returns all fully-labeled or fully-unlabeled crosslinker
        combinations, and enforces a type-check to ensure the isotope states
        of the identified link are identical.
        '''

        if all(i == isotopestates[0] for i in isotopestates):
            length = len(isotopestates)
            return (tuple(it.repeat(i, length)) for i in self.isotopestates)

        else:
            return iter(range(0))

    #      HELPERS

    def _isotopechecker(self, item):
        '''Converts the generator type to list to avoid exhaustion'''

        if isinstance(item, types.GeneratorType):
            return list(item)
        return item


# OBJECTS
# -------


@sequence.serializable("IsotopeLabeledCrosslink")
class IsotopeLabeledLink(namedtuple("IsotopeLabeledLink",
    "index sequenced frozen states file")):

    #      HELPERS

    def getheaders(self, profile):
        return [profile.getheader(i.populations) for i in self.states]

    def getspreadsheet(self, data):
        return data['spreadsheet']['crosslinks'][self.index]

    def getcrosslink(self, data):
        return data['crosslinks'][self.index]

    def getdataindexes(self, data):
        return data['crosslinks'][self.index].index


@sequence.serializable("IsotopeLabeledState")
class IsotopeLabeledState(namedtuple("IsotopeLabeledState",
    "modifications mass populations crosslinker")):
    '''# TODO: Doc'''


# CALCULATOR
# ----------


@logger.init('quantitative', 'DEBUG')
class GetLabeledCrosslinks(base.BaseObject):
    '''
    Calculates the isotope-labeled states, including with modifications
    and base formula for each crosslink.
    '''

    def __init__(self, row):
        super(GetLabeledCrosslinks, self).__init__()

        self.row = row
        self.engine = row.engines['matched']

        source = self.app.discovererthread
        self.profile = source.parameters.profile
        self.modifications = source.parameters.modifications

        self.permutations = CalculateIsotopePermutations()
        self.freezer = frozen.LabeledCrosslinkFreezer.fromrow(row)

    def __call__(self, crosslinkindex, crosslink, isotopedata):
        '''
        Returns each permutation of the isotope-labeled crosslinkers
        in a generator.
        '''

        isotopestates, experimental, theoretical = ZIP(*isotopedata)
        permutations = self.permutations(isotopestates)
        zipped = list(ZIP(theoretical, experimental))

        states = list(self.getstates(crosslink, permutations, zipped))
        if states:
            frozen = self.freezer(crosslinkindex, states)

            return IsotopeLabeledLink(
                crosslinkindex,
                isotopestates,
                frozen,
                states,
                self.row.index)

    #      GETTERS

    def getstates(self, crosslink, permutations, zipped):
        '''Yields all the theoretical isotope states for the peptide'''

        for populations in permutations:
            modifications = list(self.getmodifications(populations, zipped))
            mass = self.getmass(modifications, populations, crosslink)

            yield IsotopeLabeledState(modifications,
                mass,
                populations,
                # ASSUMPTION: assumes only a single crosslinker per state,
                # which, is a safe assumption
                self.profile.populations[populations[0]].crosslinker)

    def getmodifications(self, populations, zipped):
        '''Returns a new modification dict for each peptide in zipper'''

        for index, (theoretical, experimental) in enumerate(zipped):
            modification = matched.Modification.new()

            # grab index for theoretical isotope labels and add them
            population = populations[index]
            modification['certain'].update(theoretical[population].positions)
            modification['certain'].update(experimental.standard)

            # replace the crosslinker fragments with template ones
            fragments = self.replace_fragments(
                population, experimental.crosslinker)
            modification['certain'].update(fragments)

            yield modification

    def getmass(self, modifications, populations, crosslink):
        '''Calculate the new mass of the crosslinked peptide'''

        crosslinker = self._getcrosslinker(populations[0])
        masser = masstools.CrosslinkedMass(self.row, crosslinker)

        peptides = self.row.data.getcolumn(crosslink.index, 'peptide')
        zipped = ZIP(peptides, modifications)
        formulas = (masstools.getpeptideformula(*i, engine=self.engine)
                    for i in zipped)

        return masser.getpeptidemass(crosslink.ends, formulas, modifications)

    def _getcrosslinker(self, population):
        return self.profile.populations[population].getcrosslinker()

    #      HELPERS

    def replace_fragments(self, population, fragments):
        '''
        Replaces the crosslinker fragment modifications with new
        modifications in the profile.
        '''

        # get the crosslinker -> fragments -> new fragment name
        crosslinker = self._getcrosslinker(population)
        newname = self.modifications[crosslinker.fragments[0]].name

        # add all the positions to the same new fragment
        newfragments = defaultdict(list)
        for positions in fragments.values():
            newfragments[newname] += positions

        return newfragments
