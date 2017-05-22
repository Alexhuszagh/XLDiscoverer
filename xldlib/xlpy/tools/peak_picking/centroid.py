'''
    XlPy/Tools/Peak_Picking/centroid
    ________________________________

    Elucidate if a peak is centroided and centroid it if it is not

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import numpy as np
from scipy import integrate

from xldlib.definitions import ZIP


# CONSTANTS
# ---------
CENTROIDED_THRESHOLD = 0.05


# CHECKERS
# --------


def check_centroided(intensity):
    '''Detects whether the file has centroided or profile-type peaks.'''

    # break if not enough values
    assert intensity.size > 5
    # check to see if a good percentage of intensities are 0
    # high percentage means not centroided
    indexes, = np.where(intensity == 0.)
    return (indexes.size / intensity.size) < CENTROIDED_THRESHOLD


def find_peaks(x, y, baseline=0.):
    '''
    Returns a generator with m/z and intensity arrays corresponding
    to individual peaks.

    >>> x = np.array([351.95169, 351.95294, 351.95419, 351.95544,
    ...     351.95668, 351.95793, 351.95918, 351.96042, 351.96167, 351.96292,
    ...     351.96416, 351.96541, 351.96666])
    >>> y = np.array([0.0, 0.0, 0.0, 415.131, 763.698, 1136.421, 1729.902,
    ...     2430.958, 2676.107, 2086.312, 915.789, 0.0, 0.0])
    >>> [[i.tolist() for i in item] for item in find_peaks(x, y)]
    [[[351.95419, 351.95544, 351.95668, 351.95793, 351.95918, 351.96042, 351.96167, 351.96292, 351.96416], [0.0, 415.131, 763.698, 1136.421, 1729.902, 2430.958, 2676.107, 2086.312, 915.789]]]
    '''

    if not isinstance(x, np.ndarray):
        x = np.array(x)
    if not isinstance(y, np.ndarray):
        y = np.array(y)

    baseline, = np.where(y <= baseline)
    x = (i for i in np.split(x, baseline) if i.size > 1)
    y = (i for i in np.split(y, baseline) if i.size > 1)
    return ZIP(x, y)


def centroid_peak(x, y):
    '''
    Centroid an x,y array pair and return an x and y value. Weights
    the centroiding based off the intensity of the y values.

    >>> x = np.array([351.95419, 351.95544, 351.95668, 351.95793, 351.95918,
    ...     351.96042, 351.96167, 351.96292, 351.96416])
    >>> y = np.array([0., 415.131, 763.698, 1136.421, 1729.902, 2430.958,
    ...     2676.107, 2086.312, 915.789])
    >>> centroid_peak(x, y)
    (351.96059175911802, 14.578820424997993)
    '''

    # take weighted average for positions, cumtrapz for heights
    x_out = np.average(x, weights=y)
    y_out = integrate.cumtrapz(y, x=x)[-1]

    return x_out, y_out


def centroid_scan(mz, intensity):
    '''
    Finds all the peaks and centroids each peak, reconstructing a peaklist
    from the centroided values.
    '''

    peaks = find_peaks(mz, intensity)
    centroided = (centroid_peak(*i) for i in peaks)
    flat = (i for item in centroided for i in item)
    flattened = np.fromiter(flat, dtype=float)

    return flattened[::2], flattened[1::2]
