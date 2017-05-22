'''
    Utils/math_/array
    _________________

    Tools to normalize, remove self-propogating values numpy arrays.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from __future__ import division

import numpy as np


# HELPERS
# -------


def spacing(bins, mode='max'):
    '''
    Calculates the max width between adjacent values in numpy array.
    :
        spacing(np.array(range(20))) -> 1
        spacing(np.array(range(0, 20, 2))) -> 2
    '''

    bins = np.array(bins)
    return getattr((bins[1:] - bins[:-1]), mode)()


def finite(*arrays):
    '''
    Removes all associated data where the data is (np.nan, np.inf)
    with number elements.
    :
        array = np.array([np.nan, np.inf, 5, 10, np.nan, 20])
        finite(array)->[5., 10., 20.]
    '''

    arrays = tuple(np.array(i) for i in arrays)
    # ensure all arrays linked arrays are properly so
    assert len(arrays) > 0 and all(i.size == arrays[0].size for i in arrays)
    isfinite = np.isfinite(arrays[0])
    return tuple(i[isfinite] for i in arrays)


def to_num(array):
    '''
    Replaces all the non-number elements in an array (np.nan, np.inf)
    with number elements.
    :
        array = np.array([np.nan, np.inf, 5, 10, np.nan, 20])
        to_num(array)->[5., 10., 20.]
            -> array([0, 1.79769313e+308, 5, 1, 0, 20])
    '''

    return np.nan_to_num(np.array(array))


def normalize(array):
    '''
    Normalizes a vector to be bound from -1->0->1 (we deal in
    positive space). First converts all non-numbers to numbers.
    :
        array = np.array([np.nan, 5, 10, np.nan, 20])
        normalize(array) ->array([0., 0.25, 0.5, 0., 1.])    # Python3 division
    '''

    array = to_num(array)
    if not array.any():
        return array
    else:
        return array / array.max()
