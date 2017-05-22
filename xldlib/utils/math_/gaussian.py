'''
    Utils/math_/gaussian
    ____________________

    Tools for calculating gaussian fitting functions and fit correlations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import numpy as np
from scipy import optimize, stats as spstats

from xldlib import exception
from . import functions, stats


# HELPERS
# -------


def fit_estimate(x, y):
    '''
    Quickly estimates the parameters of a gaussian given the bins
    and hists of the function. Uses the Sheppard's Approximation
    to estimate the variance
    '''

    height = y.max()
    counts = y.sum()
    weight = x * y

    with np.errstate(invalid='raise'):
        try:
            mean = weight.sum() / counts
        except FloatingPointError:
            mean = x.mean()

    # estimate sigma via Sheppard's approximation
    sigma = stats.sheppards(x, y)

    return height, mean, sigma


@exception.silence_warning(RuntimeWarning)
def spanning_gaussian(x, *p):
    '''
    Returns a gaussian if the gaussian spans most of the current
    window, otherwise, throws astronomically high values back.
    '''

    # estimate distribution and grab mins and max
    y = functions.gaussian(x, *p)
    mins = y[[0, -1]]
    max_ = y.max()
    # check if values span regions, IE, baseline > 30% valley
    if any(i / max_ > 0.3 for i in mins):
        y = y * np.inf

    return y


def get_theoretical_gaussian(x, y, iterative=False):
    '''
    Processes and produces a theoreitcal gaussian given a set
    of bins (x values) and hists (y values). Quickly fits a gaussian
    and uses this to estimate fit with the experimental data.
    '''

    p = fit_estimate(x, y)
    if iterative:
        p, var = optimize.curve_fit(spanning_gaussian, x, y, p0=p0, maxfev=800)
    return functions.gaussian(x, *p)



# FIT
# ---


def fit_gaussian(x, y):
    '''
    Checks the distribution fit to a theoretical gaussian
    profile using pearson's coefficient. Estimates the parameters to
    optimize the fit via a quick estimate, allowing fast gaussian modeling.
    '''

    try:
        if x.size > 4:
            gaussian = get_theoretical_gaussian(x, y)
            fit, pvalue = spstats.pearsonr(gaussian, y)

            # need to ensure it's within 0 -> 1 range
            return min(max(np.nan_to_num(fit), 0), 1)
        else:
            return 0
    except RuntimeError:
        return 0
