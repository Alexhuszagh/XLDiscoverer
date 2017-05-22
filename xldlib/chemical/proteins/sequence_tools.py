'''
    Chemical/Proteins/sequence_tools
    ________________________________

    Toolkit for working with protein sequences for spectral libraries.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import random

import six

import tables as tb

#from xldlib.resources.parameters import defaults

__all__ = [
    'cut_sequence',
    'make_decoy',
]


# ENUMS
# -----


DECOY_MODES = tb.Enum([
    'reversed',
    'shuffled'
])


# DECOYS
# ------


def make_decoy(sequence, mode='reversed', seed=True):
    '''
    Create decoy sequence for concatenated database creation
    and false hit filtering.

    Args:
        sequence (str): protein sequence
        mode (enum):
            0 -- MS/MS mode (reversed sequence)
            1 -- Peptide mass fingerprinting mode (shuffled)
        seed (bool):    Seed when shuffling sequence
    '''

    if _modechecker(mode) == 0:
        return sequence[::-1]

    else:
        seq = list(sequence)
        if seed:
            # in Python 2 and 3, random.seed(hashable) is consistent and
            # independent of PYTHONHASHSEED, although order differs 2 to 3
            random.seed(sequence)

        random.shuffle(seq)
        return ''.join(seq)


# PROTEASES
# ---------


def cut_sequence(sequence, protease, nonspecific=False):
    '''
    Cut target sequence into proteolytic peptides
    # TODO: needs to consider N- and C-terminal non-specific cleavages
    '''

#    if nonspecific is None:
#        nonspecific = defaults.DEFAULTS['nonspecific_cleavage']

    start = 1

    while sequence:
        cut = protease.cut_peptide(sequence)

        yield (cut.peptide, start, 0)
        start += cut.position
        sequence = cut.remaining


# PRIVATE
# -------


def _modechecker(mode):
    '''Normalize DECOY_MODES enumerated values'''

    if isinstance(mode, six.string_types):
        return DECOY_MODES[mode]
    return mode
