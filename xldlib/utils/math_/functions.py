'''
    Utils/Math_/functions
    _____________________

    Standard peak approximation functions for peak fitting.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import numpy as np

from xldlib import exception

# load objects/functions
from xldlib.definitions import partial


# NORMAL
# ------


def gaussian(x, *p):
    '''Returns a gaussian function the x values and a given guess.'''

    height, mean, sigma = p
    return height * np.exp(-(x - mean) ** 2 / (2.* sigma ** 2))


@exception.silence_warning(RuntimeWarning)
def lorentzian(x, *p):
    '''Returns a lorentzian function with the x values and the given guess.'''

    height, mean, fwhm = p
    hist = height * fwhm ** 2 / ((x - mean) ** 2 + fwhm ** 2)
    if hist.min() < 0:
        # throw astronomically large value if negative -- bounds
        hist = hist * np.inf
    return hist


@exception.silence_warning(RuntimeWarning)
def pvoigt(x, *p):
    '''Returns a pseudo-voigt function the x values and a given guess.'''

    height, mean, sigma, fraction = p
    gauss = partial(gaussian, x, 1, mean, sigma)
    loren = partial(lorentzian, x, 1, mean, sigma)

    if fraction < 0 or fraction > 1:
        # set bounds via astronomically high values if out of bounds
        y = x * np.inf
    else:
        # estimate distribution
        y = height * ((1 - fraction) * gauss() + fraction * loren())
        if y.min() < 0:
            y = y * np.inf

    return y
