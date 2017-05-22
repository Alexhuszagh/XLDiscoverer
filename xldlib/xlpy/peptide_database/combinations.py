'''
    XlPy/Peptide_Database/combinations
    __________________________________

    Generates theoretical crosslink fragment combinations from
    the given crosslinker fragments, and assigns the basemods
    for further permutations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from __future__ import division

import itertools as it

from xldlib import chemical
from xldlib.general import mapping


# COMBINATIONS
# ------------


class FragmentCombinations(object):
    '''
    Inheritable with multiple methods for iterating over fragment cpombos.
    '''

    precision = 7

    def get_fragment_masses(self):
        '''Returns a dictionary with crosslink fragment {name: mass}'''

        fragments = self.xler['fragments']
        names = fragments['name']
        formula = fragments['formula']
        react = fragments['reactivity']
        masses = mapping.OrderedDefaultdict(list)

        for index, name in enumerate(names):
            mass = round(chemical.Molecule(formula[index]), self.precision)
            masses[(mass, react[index])].append(name)

        return masses

    def organize_basemods(self):
        '''Returns a dictionary with {res: (name, mass)}'''

        names = self.mods['Mod Name']
        formulas = self.mods['Formula']
        react = self.mods['Reactivity']
        basemods = mapping.OrderedDefaultdict(list)

        for index, name in enumerate(names):
            res = react[index]
            formula = formulas[index]
            basemods[res].append((name, formula))

        return basemods

    def get_fragment_combinations(self, count, res=True):
        '''
        Returns all the fragment combinations for a given mass. Since the
        mass order does not matter, and each can be sampled with replacement,
        it follows as the number of combinations with replacement.
        :
            self.get_fragment_combinations(2, res=False)->
                [(54.011, 54.011), (54.011, 85.983), (54.011, 103.993),
                 (85.983, 85.983), (85.983, 103.993), (103.993, 103.993)]
            self.get_fragment_combinations(2, res=True)->
                [((54.011, 'K'),), ((85.983, 'K'),), ((103.993, 'K'),)]
        '''

        if res:
            keys = self.fragment_masses.keys()
        else:
            keys = (i[0] for i in self.fragment_masses.keys())
        return it.combinations_with_replacement(keys, count)
