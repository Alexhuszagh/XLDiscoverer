'''
    XlPy/matched/sequence_variants
    ______________________________

    To limit search database size with sequence_variants, Mascot and
    other search engines use amino acid substitution with placeholders,
    as defined by (regex notation):
    :
        'B' -> 'D|N'
        'Z' -> 'E|Q'
        'X' -> '*'

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import itertools as it

from xldlib import chemical
from xldlib.chemical import building_blocks
from xldlib.resources.parameters import defaults
from xldlib.utils import masstools


# CONSTANTS
# ---------
RESIDUE_MASSES = {i: chemical.Molecule(peptide=i).mass
                  for i in building_blocks.ONE_LETTER}

SUBSTITUES = {
    'B': {'D', 'N'},
    'J': {'I', 'L'},
    'X': set(building_blocks.ONE_LETTER),
    'Z': {'E', 'Q'}
}


# HELPERS
# -------


def get_substitution_events(peptide):
    '''Finds the substitute residues and replaces these instances'''

    replace = []
    for index, residue in enumerate(peptide):
        if residue in SUBSTITUES:
            replace.append((residue, index))
    replace.sort()

    return list(zip(*replace))



class SubstitutePlaceholders(object):
    '''
    Provides a callable method to replace the various placeholders used
    by peptide search engines such as Mascot to simplify the search
    space upon dealing with sequence variants, such as D/N, E/Q, and
    highly variable sequence variants (X, for unknown).

    Features lazy evaluation.
    '''
    # maximum number of X substitutions before discarding ID,
    # high sequence variability is typically in redundant sequences of
    # large MW proteins, and therefore poor IDs.
    __max_mascot_x = 4

    def __init__(self, engine):
        super(SubstitutePlaceholders, self).__init__()

        self.engine = engine

    def __call__(self, row):
        '''
        On call, calculates all satisfactory replacements using a memoized
        cartesian product, to reduce the search space.
        '''

        peptide = list(row['peptide'])
        if peptide.count('X') > self.__max_mascot_x:
            # TODO: need to not drop peptides with such high values, but rather
            # reduce the combination space
            return []

        replacement_events = get_substitution_events(peptide)
        if replacement_events:
            return self.replace_placeholders(peptide, row, *replacement_events)

        else:
            return [''.join(peptide)]

    def replace_placeholders(self, base_peptide, row, replace, indexes):
        '''Replaces the given placeholder residues via lazy evaluation'''

        args = map(SUBSTITUES.get, replace)
        basemass = self.get_mass(base_peptide, row['modifications'])

        # use the pre-mapped combinaitons to lower the actual search time
        # O(1) lookup times for each pre-used combination, but can
        # sample all permutations
        rejected = set()
        accepted = set()
        for combination in it.product(*args):
            # memoization is on 5e-7 time, calculation is on 1-6...
            # but, memoization reduces search space ~94%, leading to ~2x
            # performance improvements
            immutable = tuple(sorted(combination))
            if immutable in accepted:
                yield self.get_peptide(base_peptide, indexes, combination)

            elif immutable in rejected:
                continue

            else:
                if self.is_below_ppm(basemass, row, combination):
                    accepted.add(immutable)
                    yield self.get_peptide(base_peptide, indexes, combination)

                else:
                    rejected.add(immutable)

    #     GETTERS

    def get_mass(self, peptide, modifications):
        '''
        Returns the theoretical mass for the peptide with all modifications
        '''

        base_peptide = ''.join(i for i in peptide if i in RESIDUE_MASSES)
        return masstools.getpeptideformula(base_peptide, modifications,
            self.engine, with_crosslinkers=True).mass

    def get_peptide(self, base_peptide, indexes, combination):
        '''Processes the replacement events the acquire the theoretical pep'''

        peptide = base_peptide[:]
        for idx, index in enumerate(indexes):
            peptide[index] = combination[idx]

        return ''.join(peptide)

    #     CHECKERS

    def is_below_ppm(self, basemass, row, combination):
        '''Returns the ppm for a row from a given basemass for the peptide'''

        mass = sum(RESIDUE_MASSES[i] for i in combination)
        ppm = masstools.ppm(row['mz'], row['z'], basemass + mass)
        return abs(ppm) < defaults.DEFAULTS['ppm_threshold']
