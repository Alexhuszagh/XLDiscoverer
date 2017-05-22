'''
    XlPy/Peptide_Database/mods
    __________________________

    Expands the theoretical mods and creates compact, compressed arrays
    which are easily convertible for vectorized link searching.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import itertools

from collections import Counter, namedtuple

from models.params.residues import RESIDUE_TYPES

from xldlib import chemical
from xldlib.utils import iterables

from .combinations import FragmentCombinations



# ------------------
#    MOD OPTIONS
# ------------------


class HDf5Processing(FragmentCombinations):
    '''Converts the Pythonic datatypes to HDF5 compatible ones'''

    def get_formula(self, mod_perm, index):
        '''
        Calculates the theoretical formula from the mod permutations
        and the current XL fragments and peptide.
        '''

        sequence = self._peptides[index].decode('utf-8')
        formula = chemical.Molecule(peptide=sequence)
        formulas = Counter(i[1] for item in mod_perm for i in item)

        for mod_formula, count in formulas.items():
            formula.update_formula(mod_formula, count=count)

        return formula

    def get_mods(self, res_list, mod_perm):
        '''
        Extracts the mod lists, include fragment mods, from the modified
        residues and the mod permutations, and then creates a matrix from
        them.
        '''

        mods_names = [i[0] for item in mod_perm for i in item]
        modpos = list(zip(mods_names, res_list))

        # need to separate the clustered mods, like Met-loss+Acetly
        modpos = [(i, res) for item, res in modpos for i in item.split('+')]
        xler_mods = [(self.fragment_masses[i][0], i[1]) for i in self._combo]
        modpos += xler_mods
        return self.convert_mods(modpos)

    def convert_mods(self, modpos):
        '''Converts the modification to integer IDs for simplified storage'''

        # don't need to worry about base2 flags because no position, just
        # mod counts.
        mods, res_list = zip(*modpos)
        string = '{:%s}' % self.mods_length
        mods = ''.join(string.format(self.mod_ids[i]) for i in mods)
        mods = mods.encode('utf-8')

        return mods


class Permutations(object):
    '''
    Tools to iterate over and expand given permutations for mod combinations.
    '''

    def attach_basemods(self, index):
        '''
        Iterates over all base_mod possibilities and then attaches
        them to the target sequence to make a list of searchables.
        '''

        res_permutations, order = self.get_residue_permutations(index)
        for res_perm in res_permutations:
            # now need to calculate each mod permutation
            mod_permutations = []
            for idx, count in enumerate(res_perm):
                res = order[idx]
                mod_permutations.append(self.get_mod_permutations(res, count))
            mod_permutations = itertools.product(*mod_permutations)

            # mod perm has res_tuples for res in order
            res_list = []
            for idx, count in enumerate(res_perm):
                res_list += [order[idx]] * count
            for mod_perm in mod_permutations:
                self.make_searchable(res_list, mod_perm, index)

    def get_residue_permutations(self, index):
        '''Grabs all residue permutations for residues that are "modifiable"'''

        seq = self._peptides[index].decode('utf-8')
        basemod_react = {}
        for r_csv in self.basemods:
            count = sum(seq.count(r) for r in r_csv)
            # need to grab the Nterm/Cterm IDs
            for key in RESIDUE_TYPES.terms:
                if any(i in r_csv for i in RESIDUE_TYPES[key]):
                    count += 1

            # subtract actual mod positions
            count -= self._combo_react.get(r_csv, 0)
            basemod_react[r_csv] = count

        order = sorted(basemod_react)
        ranges = [range(basemod_react[i] + 1) for i in order]
        max_ = self.max_mods - self.fragments
        permutations = iterables.num_product(*ranges, max=max_)

        return permutations, order

    def get_mod_permutations(self, res, count):
        '''Grabs all residue permutations from the mod lists'''

        cwr = itertools.combinations_with_replacement
        return cwr(self.basemods[res], count)


class AddMods(HDf5Processing, Permutations):
    '''
    Base class to add various posttranslation modifications to a
    given peptide sequence during XL-MS searching, first considering
    XL modifications and then the base mods.
    '''

    fragments = None
    _peptides = None
    _starts = None

    _combo = None
    _id = None
    _combo_mass = None
    _combo_react = None

    search_fields = "id peptide start modifications formula mass"
    searchable = namedtuple("Search", search_fields)
    search_fields = searchable._fields

    # ------------------
    #      MODS
    # ------------------

    def add_mods(self):
        '''Attaches the posttranslational mods to each peptide sequence'''

        for self.fragments in range(1, self.max_xl):
            self.attach_mods()

    def attach_mods(self):
        '''
        Attachs the fragments and basemods to a given series
        of XL-MS peptides.
        '''

        grp = self.grp['peptides/{}'.format(self._mode)]
        for missed in range(self.max_missed):
            ids = grp[str(missed)]
            combinations = list(self.get_fragment_combinations(self.fragments))
            for self._id, dset in ids.items():
                self.fragment_combinations(combinations, dset)

    def fragment_combinations(self, combinations, dset):
        '''Adds the fragment combinations for a given ID'''

        for self._combo in combinations:
            self._peptides = dset['peptide'].value
            self._starts = dset['start'].value

            for index in range(self._peptides.size):
                if self.same_reactivity(index):
                    self.attach_basemods(index)

    def same_reactivity(self, index):
        '''Evals to true if all the reactive cut sites are possible'''

        self._combo_mass = [e[0] for e in self._combo]
        self._combo_react = Counter([e[1] for e in self._combo])
        # TODO: need to change for self.uncleaved or not self.uncleaved
        seq = self._peptides[index][:-1].decode('utf-8')

        react = {}
        for react_csv in self._combo_react:
            counts = sum(seq.count(r) for r in react_csv.split(','))
            react[react_csv] = counts

        if all((react[k] >= v for k, v in self._combo_react.items())):
            return True

    def make_searchable(self, res_list, mod_perm, index):
        '''Makes a namedtuple searchable instance'''

        mods = self.get_mods(res_list, mod_perm)
        formula = self.get_formula(mod_perm, index)
        mass = formula.mass + sum(self._combo_mass)

        start = self._starts[index]
        seq = self._peptides[index]
        if self._mode == 'decoy':
            id_ = b'decoy'
        else:
            id_ = self._id.encode('utf-8')
        str_form = formula.tostr().encode('utf-8')

        search = self.searchable(id_, seq, start, mods, str_form, mass)
        self.set_item(search)

    def set_item(self, search):
        '''Sets the item and linearizes if necessary'''

        key = tuple(sorted(e for e in self._combo_mass))
        searchables = self.searchables[self._mode][key]
        searchables.append(search)

        if len(searchables) == 1000:
            key = '{}/{}'.format(self._mode, key)
            self.linearize_key(key, searchables)
