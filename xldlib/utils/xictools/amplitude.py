'''
    Utils/Xictools/amplitude
    ________________________

    Tools for processing extracted ion chromatogram amplitudes and
    metadata.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import itertools as it

import numpy as np
from scipy import integrate
import tables as tb

from xldlib import exception

# load objects/functions
from collections import namedtuple

from .metrics import Metrics


# ENUMS
# -----

SPECTRAL_ENUM = tb.Enum({
    'Area': "area",
    'Intensity': "ymax"
})

INTEGRAL_ENUM = tb.Enum({
    'Included Charges': "charges",
    'Integrated PPM': "ppm"
})


# DATA
# ----

XRANGE_KEYS = (
    'Min Window',
    'Max Window'
)

# OBJECTS
# -------

WeightedPpm = namedtuple("WeightedPpm", "ppm weight")


class ValueRange(namedtuple("ValueRange", "min max")):
    '''Definitions for array value ranges'''

    #  CLASS METHODS

    @classmethod
    def xrange_fromdict(cls, spreadsheet, header, keys=XRANGE_KEYS):
        return cls(*(spreadsheet[(header, k)] for k in keys))

    #     PUBLIC

    def iterfields(self, suffix=' Window'):
        '''Yields a key-value pairwise iterator to flatten the data'''

        for key, value in self._asdict().items():
            yield key.capitalize() + suffix, value


class Amplitude(namedtuple("Amplitude", "name value baseline")):
    '''Definitions for spectral amplitude with an implicit baseline'''

    # CONVERSIONS
    # -----------
    prefix = 'Minimum '

    def __new__(cls, name, value, baseline=float('nan')):
        return super(Amplitude, cls).__new__(cls, name, value, baseline)

    #  CLASS METHODS

    @classmethod
    def fromdict(cls, obj, header, attrname):
        '''
        Initializes the amplitude (along with noise baseline) from a
        mapping structure with keys for the spectral amplitudes.
        '''

        key = SPECTRAL_ENUM(attrname)
        value = obj[(header, key)]
        baseline = obj[(header, cls.prefix + key)]
        return cls(attrname, value, baseline)

    #     PUBLIC

    def iterfields(self):
        '''Yields a key-value pairwise iterator to flatten the data'''

        name = SPECTRAL_ENUM(self.name)
        yield name, self.value
        yield self.prefix + name, self.baseline


class IntegralData(namedtuple("IntegralData", "xrange "
    "area ymax ppm charges metrics counts")):

    def __new__(cls, *args, **kwds):
        if len(args) < 7:
            kwds.setdefault('counts', None)
        return super(IntegralData, cls).__new__(cls, *args, **kwds)

    #  CLASS METHODS

    @classmethod
    def fromspreadsheet(cls, spreadsheet, header, counts=None):
        '''Converts spreadsheet data back to an IntegralData instance'''

        xrange_ = ValueRange.xrange_fromdict(spreadsheet, header)
        area = Amplitude.fromdict(spreadsheet, header, 'area')
        ymax = Amplitude.fromdict(spreadsheet, header, 'ymax')
        ppm = spreadsheet[(header, INTEGRAL_ENUM('ppm'))]
        charges = spreadsheet[(header, INTEGRAL_ENUM('charges'))]
        metrics = Metrics.fromspreadsheet(spreadsheet, header)

        return cls(xrange_, area, ymax, ppm, charges, metrics, counts)

    #     PUBLIC

    def iterfields(self):
        '''Yields a key-value pairwise iterator to flatten the data'''

        xrange_ = self.xrange.iterfields()
        area = self.area.iterfields()
        ymax = self.ymax.iterfields()
        for item in it.chain(xrange_, area, ymax):
            yield item
        for key, attrname in INTEGRAL_ENUM:
            yield key, getattr(self, attrname)


class IntegratedData(namedtuple("IntegratedData", "area ymax")):
    '''Definitions for integrated spectral data'''

    #  CLASS METHODS

    @classmethod
    def fromcrosslink(cls, crosslink, usedcharges=()):
        '''Initializes a new integrated dataset from a crosslink'''

        start, end = crosslink.get_peak_indexes()
        x = crosslink.get_retentiontime(start, end)
        standard = getintegral(x, crosslink, start, end)
        noise = getnoiseintegral(x, crosslink, start, end, usedcharges)

        area = Amplitude('area', standard.area, noise.area)
        ymax = Amplitude('ymax', standard.ymax, noise.ymax)
        return cls(area, ymax)


# HELPERS
# -------


@exception.silence_warning(RuntimeWarning)
def weighted_ppm(x, xdefault, weights=None):
    '''
    Calculates a weighted arithmetic mean for the difference between
    x (scalar, scalar array) and xdefault (scalar), with an optional
    weights parameter.
    '''

    xdiff = ((x - xdefault) / xdefault) * 1e6
    try:
        return np.average(xdiff, weights=weights)
    except ZeroDivisionError:
        # all the weights sum to 0
        return float("nan")


# FUNCTIONS
# ---------


@exception.silence_warning(RuntimeWarning)
def get_isotopeppm(isotope, bounds=None):
    '''
    Calculates the mean ppm over the start to end window
    given the precursor m/z and the m/z for each transition in
    the window.
    '''

    if bounds is None:
        crosslink = isotope.get_crosslink()
        start, end = crosslink.get_peak_indexes()
    else:
        start, end = bounds

    mz = isotope.mz()[start: end]
    isotope_mz = isotope.getattr('isotope_mz')
    intensity = isotope.intensity()[start: end]
    ppm = weighted_ppm(mz, isotope_mz, weights=intensity)

    return WeightedPpm(ppm, intensity.sum())


def get_integral(group, fun=integrate.trapz):
    '''Integrates for a singular group'''

    start, end = group.get_crosslink().get_peak_indexes()
    x = group.get_retentiontime(start, end)
    y = group.intensity()[start:end]

    return fun(y, x)


def getintegral(x, crosslink, start, end):
    '''Integrates over all selected children to calulate the XIC amplitude'''

    area = []
    ymax = 0.

    if crosslink.getattr('checked'):
        for charge in crosslink.get_selected():
            for isotope in charge.get_selected():
                y = isotope.intensity()[start:end]

                area.append(integrate.trapz(y, x))
                ymax = max(ymax, y.max())

    if not area:
        return IntegratedData(float('nan'), float('nan'))
    else:
        return IntegratedData(sum(area), ymax)


def getnoiseintegral(x, crosslink, start, end, usedcharges):
    '''
    Integrates over the maxmimum set of selected children to
    calulate the XIC amplitude
    '''

    area = []
    ymax = 0.

    charges = (crosslink[i] for i in usedcharges)
    for charge in charges:
        for isotope in charge:
            y = isotope.intensity()[start:end]

            area.append(integrate.trapz(y, x))
            ymax = max(ymax, y.max())

    if not area:
        return IntegratedData(float('nan'), float('nan'))
    else:
        return IntegratedData(sum(area), ymax)


def get_ppm(crosslink, start, end):
    '''Returns the weighted ppms for each isotope averaged'''

    zipped = []
    for charge in crosslink.get_selected():
        zipped.extend(i.get_ppm((start, end)) for i in charge.get_selected())

    if zipped:
        ppms, weights = zip(*zipped)
        if any(weights):
            # not any(weights) -> ZeroDivisionError
            return np.average(ppms, weights=weights)
    # no checked values // no weights
    return float("nan")


def xic_data(crosslink, usedcharges=()):
    '''Finds the used charges, ppm, and integral for the XIC'''

    start, end = crosslink.get_peak_indexes()
    rt = crosslink.get_retentiontime()
    xrange_ = ValueRange(rt[start], rt[end])

    integrated = IntegratedData.fromcrosslink(crosslink, usedcharges)

    return IntegralData(xrange_,
        integrated.area,
        integrated.ymax,
        crosslink.get_ppm(start, end),
        crosslink.get_checkedcharges(),
        Metrics.fromcrosslink(crosslink))
