'''
    Chemical/Proteins/protein
    _________________________

    Object definitions for proteins.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from namedlist import FACTORY, namedlist

from xldlib import chemical

from .peptide_list import PeptideListMixin, Peptides
from .sequence_tools import make_decoy

__all__ = [
    'Protein'
]

# CONSTANTS
# ---------

DECOY_ID = 'decoy'
DECOY_MENMONIC = 'DECOY_DECOY'

# DATA
# ----

UNIPROT_FIELDS = {
    'sequence': ('Sequence', slice(None)),
    'name': ('Gene names  (primary )', slice(None)),
    'id': ('Entry', slice(None)),
    'mnemonic': ('Entry Name', slice(None))
}

FASTA_FIELDS = {
    'sequence': ('sequence', slice(None)),
    'name': ('description', slice(None)),
    'id': ('sp', 0),
    'mnemonic': ('sp', 1)
}


# OBJECTS
# -------


class Protein(namedlist("Protein", [
    'sequence',
    'name',
    ('id', None),
    ('mnemonic', None),
    ('peptides', FACTORY(Peptides)),
]), PeptideListMixin):
    '''Protein definitions'''

    #   PROPERTIES

    @property
    def length(self):
        return len(self.sequence)

    @property
    def mw(self):
        return chemical.Molecule(peptide=self.sequence, strict=False).mass

    #  CLASS METHODS

    @classmethod
    def from_uniprot(cls, entry):
        '''Initialize class from a UniProt KB query'''

        return cls.from_dict(entry, UNIPROT_FIELDS)

    @classmethod
    def from_fasta(cls, entry):
        '''Initialize class from a FASTA or UniProt KB XML file'''

        return cls.from_dict(entry, FASTA_FIELDS)

    @classmethod
    def from_dict(cls, entry, names=None):
        '''
        Initialize class from a database query, with fields as
        `names` mapping Protein fields to the `entry` keys.

        Args:
            entry (mapping):    database record for a single protein
            names (dict, None): maps entry keys to protein fields
        '''

        if names is not None:
            return cls(**{k: entry[v][s] for k, (v, s) in names.items()})
        return cls(**entry)

    #    PUBLIC

    def sequencing_peptides(self, protease=None):
        '''Create sequencing peptides and bind to class'''

        self.cut_sequence(protease)
        self.concatenate()

    def decoy(self, mode='reversed', in_place=False):
        '''
        Create decoy protein object, and modify `in_place` or return
        copy.
        Args:
            mode (enum):        {'reversed', 'shuffled'}
            in_place (bool):    mode object in place or make copy
        '''

        sequence = make_decoy(self.sequence, mode)
        if not in_place:
            return type(self)(sequence, self.name, DECOY_ID, DECOY_MENMONIC)

        self.sequence = sequence
        self.id = DECOY_ID
        self.mnemonic = DECOY_MENMONIC
