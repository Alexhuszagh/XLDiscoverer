'''
    XlPy/Peptide_Database/decoy
    ___________________________

    Generates (optionally) stable decoy peptide sequences from a
    target protein sequence.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import random


def shuffle_sequence(sequence, seed=False):
    '''
    Randomizes a protein sequence and shuffles it for peptide mass
    fingerprint decoys.
    '''

    seq = list(sequence)
    if seed:
        # in Python 2 and 3, random.seed(hashable) is consistent and
        # independent of PYTHONHASHSEED, although order differs 2 to 3
        random.seed(sequence)

    random.shuffle(seq)
    return ''.join(seq)
