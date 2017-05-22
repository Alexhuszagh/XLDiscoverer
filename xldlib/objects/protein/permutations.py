'''
    Objects/Protein/permutations
    ____________________________

    Post-translation modification permutations from a given peptide
    or protein sequence.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.qt.objects import base


# OBJECTS
# -------


class VariableModCombinations(base.BaseObject):
    '''Definitions for variable post-translational modifications'''

    def __init__(self):
        super(VariableModCombinations, self).__init__()


class CrosslinkerPermutations(base.BaseObject):
    '''Definitions for crosslinker post-translation modifications'''

    def __init__(self):
        super(CrosslinkerPermutations, self).__init__()

        self.set_fragmentrange()

    #    SETTERS

    def set_fragmentrange(self):
        '''Sets the maximum and minimum missed cleavages to define a range'''


class ModificationPermutations(base.BaseObject):
    '''Definitions for post-translation modification permutations'''

    def __init__(self):
        super(ModificationPermutations, self).__init__()

        self.variable = VariableModCombinations()
        self.crosslinkers = CrosslinkerPermutations()
