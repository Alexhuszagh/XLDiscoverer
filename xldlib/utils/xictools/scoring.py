'''
    Utils/Xictools/scoring
    ______________________

    Tools for scoring fit quality, as well as calculating the various
    fit quality subscores of extracted ion chromatograms.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import numpy as np
from scipy import stats

from xldlib import exception

# load objects/functions
from xldlib.definitions import ZIP


# WEIGHTING
# ---------


def get_size_weight(start, end, upper=5):
    '''Returns a weighting factor depending on the size of the cluster'''

    size = end - start
    if size >= upper:
        return 1

    else:
        return size / upper


# MASS CORRELATION
# ----------------


def get_summedcorrelation(isotopes, pattern):
    '''Sum & normalize each isotope array, then correlate to pattern'''

    intensity = np.array([sum(i) for i in isotopes])
    intensity = intensity / intensity.max()
    corr = stats.pearsonr(intensity, pattern)[0]
    return np.nan_to_num(corr)


def get_axiscorrelation(isotopes, pattern):
    '''Returns the axis-wise ratio correlations to the theoretical ratio'''

    base = next(isotopes)
    ratios = (i / base for i in isotopes)

    length = range(len(pattern) - 1)
    theoretical = [np.zeros(base.size) for i in length]
    constants = np.array([i / pattern[0] for i in pattern[1:]])
    for pattern, array in ZIP(constants, theoretical):
        array.fill(pattern)

    pearson = [np.nan_to_num(stats.pearsonr(x, y)[0])
               for x, y in ZIP(ratios, theoretical)]
    return np.mean(pearson)


def get_pointcorrelation(isotopes, pattern):
    '''Returns the Pearson correlation for each point averaged'''

    zipped = ZIP(*isotopes)
    arrays = (np.array(i) for i in zipped)
    adjusted = (i / i.max() for i in arrays)
    corrs = (stats.pearsonr(i, pattern)[0] for i in adjusted)
    return np.mean([np.nan_to_num(i) for i in corrs])


@exception.silence_warning(RuntimeWarning)
def get_masscorrelation(isotopes, pattern, mode=0):
    '''
    Returns the pearsonr correlation between the experimental and
    theoretical isotope distribution.

        mode -- mass correlation calculation mode
            0 -- summed
            1 -- pearson({a1, ... an} / {b1, ... bn} , {c1, ... cn})
                where a and b are arrays of variables, and c is
                an array of constants corresponding to the expected
                ratio in the mass correlation
                    High variability means -> small pearsonr
            2 -- point-by-point average

    Features either a "summed" feature, where each array is summed prior
    to the isotope correlation, or each point calculates a pearsonr
    independently.

    Summing, as well as providing performance enhancements, better
    aggregates the data to avoid spurious correlations.
    '''

    if mode == 0:
        return get_summedcorrelation(isotopes, pattern)
    elif mode == 1:
        return get_axiscorrelation(isotopes, pattern)
    elif mode == 2:
        return get_pointcorrelation(isotopes, pattern)


# SCORING
# -------


@exception.silence_warning(RuntimeWarning)
def scorecrosslink(crosslink, dotp_weight=0.35,
                   size_weight=0.2, mass_weight=0.45):
    '''Returns the crosslink score for the extracted ion chromatograms '''

    dotp = dotp_weight * crosslink.get_dotp()
    bounds = crosslink.get_peak_indexes()
    size = size_weight * get_size_weight(bounds.start, bounds.end)
    mass = mass_weight * crosslink.get_masscorrelation()

    return sum((dotp, size, mass))
