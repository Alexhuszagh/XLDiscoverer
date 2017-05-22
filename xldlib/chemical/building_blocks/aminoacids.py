'''
    Chemical/Building_Blocks/aminoacids
    ___________________________________

    Amino acid definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import OrderedDict

from namedlist import namedlist

from xldlib.general import sequence


__all__ = [
    'AMINOACIDS',
    'ONE_LETTER',
]


# OBJECTS
# -------


@sequence.serializable('AminoAcid')
class AminoAcid(namedlist("AminoAcid", "one three name formula codons")):
    '''Definitions for aminoacid objects'''


class LowerKeyDict(OrderedDict):
    '''Transforms all keys to upper key but lower keys are still get_table'''

    #     MAGIC

    def __contains__(self, key, dict_contains=OrderedDict.__contains__):
        '''Override `__contains__` to return the transformed key'''

        return dict_contains(self, self.__transform__(key))

    def __getitem__(self, key, dict_getitem=OrderedDict.__getitem__):
        '''Override `__getitem__` to return the transformed key'''

        return dict_getitem(self, self.__transform__(key))

    def __setitem__(self, key, value, dict_setitem=OrderedDict.__setitem__):
        '''Override `__setitem__` to set the transformed key'''

        dict_setitem(self, self.__transform__(key), value)

    def __transform__(self, key):
        '''Transform the `str` of the key to the upper-case variety'''

        return key.upper()


# DATA
# ----

AMINOACIDS = LowerKeyDict([
    # 1 Letter Code: Formula
    ('A', AminoAcid(one='A',
        three='Ala',
        name='Alanine',
        formula='C3 H5 N O',
        codons=['GCU', 'GCC', 'GCA', 'GCG'])),
    ('C', AminoAcid(one='C',
        three='Cys',
        name='Cysteine',
        formula='C3 H5 N O S',
        codons=['UGU', 'UGC'])),
    ('D', AminoAcid(one='D',
        three='Asp',
        name='Aspartate',
        formula='C4 H5 N O3',
        codons=['GAU', 'GAC'])),
    ('E', AminoAcid(one='E',
        three='Glu',
        name='Glutamate',
        formula='C5 H7 N O3',
        codons=['GAA', 'GAG'])),
    ('F', AminoAcid(one='F',
        three='Phe',
        name='Phenylalanine',
        formula='C9 H9 N1 O',
        codons=['UUU', 'UUC'])),
    ('G', AminoAcid(one='G',
        three='Gly',
        name='Glycine',
        formula='C2 H3 N1 O',
        codons=['GGU', 'GGC', 'GGA', 'GGG'])),
    ('H', AminoAcid(one='H',
        three='His',
        name='Histidine',
        formula='C6 H7 N3 O',
        codons=['CAU', 'CAC'])),
    ('I', AminoAcid(one='I',
        three='Ile',
        name='Isoleucine',
        formula='C6 H11 N1 O',
        codons=['AUU', 'AUC', 'AUA'])),
    ('K', AminoAcid(one='K',
        three='Lys',
        name='Lysine',
        formula='C6 H12 N2 O',
        codons=['AAA', 'AAG'])),
    ('L', AminoAcid(one='L',
        three='Leu',
        name='Leucine',
        formula='C6 H11 N1 O',
        codons=['UUA', 'UUG', 'CUU', 'CUC', 'CUA', 'CUG'])),
    ('M', AminoAcid(one='M',
        three='Met',
        name='Methionine',
        formula='C5 H9 N1 O S',
        codons=['AUG'])),
    ('N', AminoAcid(one='N',
        three='Asn',
        name='Asparagine',
        formula='C4 H6 N2 O2',
        codons=['AAU', 'AAC'])),
    ('P', AminoAcid(one='P',
        three='Pro',
        name='Proline',
        formula='C5 H7 N1 O',
        codons=['CCU', 'CCC', 'CAA', 'CAG'])),
    ('Q', AminoAcid(one='Q',
        three='Gln',
        name='Glutamine',
        formula='C5 H8 N2 O2',
        codons=['CAA', 'CAG'])),
    ('R', AminoAcid(one='R',
        three='Arg',
        name='Arginine',
        formula='C6 H12 N4 O',
        codons=['AGA', 'AGG'])),
    ('S', AminoAcid(one='S',
        three='Ser',
        name='Serine',
        formula='C3 H5 N1 O2',
        codons=['AGU', 'AGC'])),
    ('T', AminoAcid(one='T',
        three='Thr',
        name='Threonine',
        formula='C4 H7 N1 O2',
        codons=['ACU', 'ACC', 'ACA', 'ACG'])),
    ('U', AminoAcid(one='U',
        three='Sec',
        name='Selenocysteine',
        formula='C3 H5 N1 O1 Se',
        codons=[])),
    ('V', AminoAcid(one='V',
        three='Val',
        name='Valine',
        formula='C5 H9 N1 O',
        codons=['GUU', 'GUC', 'GUA', 'GUG'])),
    ('W', AminoAcid(one='W',
        three='Trp',
        name='Tryptophan',
        formula='C11 H10 N2 O',
        codons=['UGG'])),
    ('Y', AminoAcid(one='Y',
        three='Tyr',
        name='Tyrosine',
        formula='C9 H9 N1 O2',
        codons=['UAU', 'UAC']))
])

ONE_LETTER = ''.join(AMINOACIDS)
