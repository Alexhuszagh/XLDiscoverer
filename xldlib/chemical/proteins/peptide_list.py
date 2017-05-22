'''
    Objects/Protein/peptide_list
    ____________________________

    Peptide storage list definition.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import copy
import itertools as it
import operator as op

import six

from xldlib.general import sequence
from xldlib.resources.parameters import defaults

from . import configurations as config, enzyme, peptide, sequence_tools

__all__ = [
    'PeptideListMixin',
    'Peptides',
]


# OBJECTS
# -------


class Peptides(sequence.UserList):
    '''Definition for sequential peptide storage'''

    #    PUBLIC

    def sort(self):
        '''Sort peptides by peptide start position'''

        super(Peptides, self).sort(key=op.attrgetter('start'))

    def append(self, item):
        '''Append normalized peptide to the peptide list'''

        item = self._peptidechecker(item)
        super(Peptides, self).append(item)

    #    HELPERS

    def _peptidechecker(self, item):
        '''Normalize Peptide types'''

        if isinstance(item, peptide.Peptide):
            return item

        elif isinstance(item, (list, tuple)) and len(item) > 1:
            return peptide.Peptide(*item)

        elif isinstance(item, dict) and 'sequence' in item:
            return peptide.Peptide(**item)

        else:
            raise AssertionError("Invalid Peptide object identified")


class PeptideListMixin(object):
    '''Sequential storage mixin to store peptide sequences'''

    #   PROPERTIES

    @property
    def minimum_missed(self):
        return defaults.DEFAULTS['minimum_missed_cleavages']

    @property
    def maximum_missed(self):
        return defaults.DEFAULTS['maximum_missed_cleavages']

    @property
    def missed_cleavages(self):
        return range(self.minimum_missed, self.maximum_missed + 1)

    #    PUBLIC

    def cut_sequence(self, protease=None):
        '''Cut target sequence and add proteolytic peptides to self'''

        protease = self._proteasechecker(protease)
        self.peptides.clear()
        for item in sequence_tools.cut_sequence(self.sequence, protease):
            self.peptides.append(item)
        self.peptides.sort()

    def concatenate(self):
        '''Concatenate cleaved peptide sequences for missed cleavages'''

        peptides = Peptides()
        items = it.product(enumerate(self.peptides), self.missed_cleavages)
        for (index, item), missed in items:
            if missed + index < len(self.peptides):
                # initialize new item and append to peptide buffer if valid
                new = copy.deepcopy(item)
                new.merge(*self.peptides[index+1: index+missed+1])
                if new.valid:
                    peptides.append(new)

        self.peptides = peptides

    #    HELPERS

    def _proteasechecker(self, item):
        '''Normalize ProteolyticEnzyme types'''

        if isinstance(item, enzyme.ProteolyticEnzyme):
            return item
        elif item is None:
            return enzyme.ProteolyticEnzyme()
        elif isinstance(item, (six.string_types, config.Protease)):
            return enzyme.ProteolyticEnzyme(item)
        else:
            raise AssertionError("Invalid ProteolyticEnzyme object identified")
