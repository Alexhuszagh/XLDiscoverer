'''
    Objects/Protein/enzyme
    ______________________

    Definitions for proteolytic enzyme object.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import six

from namedlist import namedlist

from xldlib.definitions import re
from xldlib.resources.parameters import defaults

from . import configurations as config


__all__ = [
    'ProteolyticEnzyme'
]


# OBJECTS
# -------

Cleaved = namedlist("Cleaved", "peptide position remaining")


class ProteolyticEnzyme(object):
    '''
    Object definition for an item that mimics a proteolytic enzyme.
    The object is a wrapper around a compiled regex, which then
    provides convenience methods for cleaving a target sequence.
    '''

    def __init__(self, enzyme=None):
        super(ProteolyticEnzyme, self).__init__()

        self.enzyme = self._enzymechecker(enzyme)
        self.cut_regex = re.compile(self.enzyme.cut_regex)

    def __repr__(self):
        '''Return representation of the cut regex for the enzyme'''

        return repr(self.cut_regex)

    #     PUBLIC

    def cut_peptide(self, sequence):
        '''
        Find first cut site and cleave sequence at cut site.

        Args:
            sequence (str):     protein sequence to cleave
        Returns (Cleaved):      cleaved peptide and remaining sequence
        '''

        match = self.cut_regex.search(sequence)
        if match is None:
            # end of the sequence, no more cuts
            return Cleaved(sequence, 0, '')

        else:
            position = match.start() + 1
            peptide = sequence[:position]
            sequence = sequence[position:]
            return Cleaved(peptide, position, sequence)

    #      HELPERS

    def _enzymechecker(self, item):
        '''Normalize Protease objects'''

        if isinstance(item, config.Protease):
            return item

        elif item is None:
            name = defaults.DEFAULTS['current_enzyme']
            return config.ENZYMES[name]

        elif isinstance(item, six.string_types):
            return config.ENZYMES[item]

        elif isinstance(item, (list, tuple)) and len(item) == 4:
            return config.Protease(*item)

        else:
            raise AssertionError("Please provides a valid protease object")
