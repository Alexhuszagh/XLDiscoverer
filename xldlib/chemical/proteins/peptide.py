'''
    Chemical/Proteins/peptide
    _________________________

    Singular peptide definition.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from namedlist import namedlist

from xldlib.resources.parameters import defaults


__all__ = [
    'Peptide'
]


# OBJECTS
# -------


class Peptide(namedlist("Peptide", [
    'sequence',
    'start',
    ('id', None),
    ('mnemonic', None),
    ('missed_cleavages', 0),
    ('modifications', None),
])):
    '''Peptide definitions.'''

    #   PROPERTIES

    @property
    def length(self):
        return len(self.sequence)

    @property
    def end(self):
        return self.start + self.length

    @property
    def minimum_length(self):
        return defaults.DEFAULTS['minimum_peptide_length']

    @property
    def maximum_length(self):
        return defaults.DEFAULTS['maximum_peptide_length']

    @property
    def valid(self):
        return self.minimum_length <= self.length <= self.maximum_length

    #    PUBLIC

    def merge(self, *other):
        '''Merge other peptide sequences with current object'''

        self.missed_cleavages += sum(i.missed_cleavages + 1 for i in other)
        self.sequence += ''.join([i.sequence for i in other])

    #    HELPERS

    def _peptidechecker(self, item):
        '''Normalize Peptide objects'''

        if isinstance(item, Peptide):
            return item
        elif isinstance(item, (list, tuple)) and len(item) > 1:
            return Peptide(*item)
        elif isinstance(item, dict) and 'sequence' in item:
            return Peptide(**item)
        else:
            raise AssertionError("Valid Peptide object not found")
