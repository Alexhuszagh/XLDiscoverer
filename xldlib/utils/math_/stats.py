'''
    Utils/math_/stats
    _________________

    Tools for calculating correlations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from __future__ import division

import numpy as np

from . import array


# P-VALUE
# -------


def sheppards(bins, hist):
    '''
    Calculates the theoretical variance for a set of binned data,
    such as spectral intensities, and then adjusts the variance based
    on h^2/12.
    '''

    # convert to num // no NaN to affect calculations
    bin_width = array.spacing(bins)
    hist = array.to_num(hist)
    # grab total hist counts and mean
    counts = hist.sum()
    weight = bins * hist
    # invalid means zeros array, ie, no intensities
    with np.errstate(invalid='raise'):
        try:
            mean = weight.sum() / counts
            # estimate variance
            var = (sum(bins ** 2 * hist) - counts * mean ** 2) / (counts - 1)
            sigma = np.sqrt(var - (bin_width ** 2 / 12))

        except FloatingPointError:
            # no intensity fallback, just skip calc and set nan
            sigma = np.nan

    return sigma


# DOT PRODUCT
# -----------


def normalized_edge_dotp(vector1, vector2):
    '''Provides standardized edge cases for the normalized_angle_sqrt'''

    if not (vector1.size and vector2.size):
        return 0
    if vector1.max() == 0 or vector2.max() == 0:
        return 0
    else:
        return normalized_angle_sqrt(vector1, vector2)


def normalized_angle_sqrt(*vectors):
    '''
    Determines the angles between two normalized vectors.
    :
        vectors -- numpy arrays

        v1 = np.array(range(20))
        v2 = np.array(range(0, 40, 2))
        normalized_angle_sqrt(v1, v2)->1

        v1 = np.array(list(range(10)) + [np.nan] + list(range(11, 20)))
        v2 = np.array(range(0, 40, 2))
        normalized_angle_sqrt(v1, v2)->0.325
    '''

    assert len(vectors) == 2
    std_vectors = []
    for vector in vectors:
        norm = array.normalize(vector)
        std_vector = np.sqrt(norm)
        std_vectors.append(std_vector)

    return angle_sqrt(*std_vectors)


def angle_sqrt(left_vector, right_vector):
    '''
    Compares the correlation of two sets of distributions
    to see if they have similar profiles based on treating them as
    vectors and calculating their dot product.

    Credit for the approach goes to Brendan McLean at Skyline:
    https://brendanx-uw1.gs.washington.edu/labkey/project/home/software/Skyline/begin.view
    License can be found in licenses/Skyline.txt
    :
        left_vector, right_vector -- numpy arrays
    '''

    sum_cross = sum(left_vector*right_vector)
    sum_left = sum(left_vector*left_vector)
    sum_right = sum(right_vector*right_vector)

    if sum_left == 0 and sum_right == 0:
        dotp = 1
    elif sum_left == 0 or sum_right == 0:
        dotp = 0
    else:
        value = sum_cross / np.sqrt(sum_left * sum_right)
        # to prevent higher than one return
        dotp = min(1, value)
    return dotp
