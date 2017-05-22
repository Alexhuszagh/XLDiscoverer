'''
    Gui/Views/Visualizer/Canvas/legends
    ___________________________________

    Generates the colored legend patches for the current plot.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np

from xldlib import exception
from xldlib.resources.parameters import defaults

# load objects/functions
from xldlib.definitions import ZIP


# HELPERS
# -------


def yield_labels(labels, indexes, plotdata):
    '''Yields the legend for the labels view'''

    profile = labels.get_document().profile
    for index, plot in ZIP(indexes, plotdata):
        crosslink = labels[index]

        populations = crosslink.populations
        yield ' - '.join(profile.populations[i].header for i in populations)


def yield_crosslink(crosslink, indexes, plotdata):
    '''Yields the legend for the crosslink view'''

    for index, plot in ZIP(indexes, plotdata):
        charge = crosslink[index]
        yield 'z = +{0}'.format(charge.levels.charge)


def yield_charge(charge, indexes, plotdata):
    '''Yields the legend for the charge view'''

    for index, plot in ZIP(indexes, plotdata):
        isotope = charge[index]
        yield next(yield_isotope(isotope, plot))


def yield_isotope(isotope, plot):
    '''Yields the legend for the isotope view'''

    if int(isotope.levels.isotope) == 0:
        yield '[M]'
    else:
        yield '[M+{0}]'.format(isotope.levels.isotope)


# LEGENDS
# -------


def get_legend(group, indexes, plotdata):
    '''Returns the text names for the current plots'''

    if group.type == 'file':
        return None
    elif group.type == 'labels':
        return list(yield_labels(group, indexes, plotdata))
    elif group.type == 'crosslink':
        return list(yield_crosslink(group, indexes, plotdata))
    elif group.type == 'charge':
        return list(yield_charge(group, indexes, plotdata))
    elif group.type == 'isotope':
        return list(yield_isotope(group, plotdata[0]))


# HELPERS
# -------


def ppm_patch(ppm, plot):
    '''Returns a ppm patch from the object'''

    if abs(ppm) < defaults.DEFAULTS['ppm_threshold']:
        return 'ppm = {:.2f}'.format(ppm)
    else:
        return 'ppm > {:3d}'.format(defaults.DEFAULTS['ppm_threshold'])


def ppm_crosslink(crosslink, indexes, plotdata, bounds):
    '''Returns the mass error at the crosslink level'''

    for index, plot in ZIP(indexes, plotdata):
        charge = crosslink[index]

        zipped = [i.get_ppm(bounds) for i in charge if i.checked]
        ppm = float("nan")
        if zipped:
            ppms, weights = zip(*zipped)
            if any(weights):
                ppm = np.average(ppms, weights=weights)

        yield ppm_patch(ppm, plot)


def ppm_charge(charge, indexes, plotdata, bounds):
    '''Returns the mass error at the charge level'''

    for index, plot in ZIP(indexes, plotdata):
        ppm = charge[index].get_ppm(bounds).ppm
        yield ppm_patch(ppm, plot)


def ppm_isotope(isotope, plot, bounds):
    '''Returns the mass error at the isotope level'''

    ppm = isotope.get_ppm(bounds).ppm
    yield ppm_patch(ppm, plot)


# PPM
# ---


@exception.silence_warning(RuntimeWarning)
def get_ppm(group, indexes, plotdata, bounds=None):
    '''Returns the PPM error as a formatted string for the current display'''

    if group.type in {'file', 'labels'}:
        return None
    elif group.type == 'crosslink':
        return list(ppm_crosslink(group, indexes, plotdata, bounds))
    elif group.type == 'charge':
        return list(ppm_charge(group, indexes, plotdata, bounds))
    elif group.type == 'isotope':
        return list(ppm_isotope(group, plotdata[0], bounds))
