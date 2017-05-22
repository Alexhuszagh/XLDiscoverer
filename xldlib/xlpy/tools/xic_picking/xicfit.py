'''
    XlPy/Tools/Xic_Picking/xicfit
    _____________________________

    Objects and functions to generate fitting arguments for XIC peak picking.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np

from xldlib.utils import math_
from xldlib.utils.xictools import scoring

# load objects/functions
from collections import namedtuple

# OBJECTS
# -------


class XicFit(namedtuple("XicFit", "x y isotopes "
    "anchors baseline noise pattern")):
    '''Subclass with bound methods for facile data processing and scoring'''

    #    YIELDERS

    def yield_dotp(self, index, start=None, end=None):
        '''Returns the dot product correlation for a given isotope'''

        isotopes = self.isotopes[index]
        monoisotopic = isotopes[0][start:end]
        other = (i[start:end] for i in isotopes[1:])

        for isotope in other:
            yield math_.normalized_edge_dotp(monoisotopic, isotope)

    #    GETTERS

    def get_meandotp(self, index, start=None, end=None):
        dotps = np.fromiter(self.yield_dotp(index, start, end), dtype=float)
        return np.mean(dotps)

    def get_masscorrelation(self, index, start=None, end=None, mode=0):
        '''Returns the mass correlation using the xictools scoring'''

        isotopes = (i[start:end] for i in self.isotopes[index])
        return scoring.get_masscorrelation(isotopes, self.pattern, mode)


# ARGUMENTS
# ---------


def get_fitargs(crosslink):
    '''
    Returns the x and y arrays, summing the y values over all identified
    charges for quantitation.
    '''

    labels = crosslink.get_labels()
    start = labels.getattr('window_start')
    end = labels.getattr('window_end')

    # grab our isotopes for dot product calculations
    charges = crosslink.get_sequencedcharges()
    y = np.sum(crosslink.charge_intensity(charges, start, end), axis=0)

    isotopes = list(crosslink.isotope_intensity(charges, start, end))

    return XicFit(crosslink.get_retentiontime(start, end),
        y,
        isotopes,
        labels.getattr('precursor_rt'),
        crosslink.get_baseline(),
        crosslink.get_noise(),
        crosslink.get_isotope_pattern())
