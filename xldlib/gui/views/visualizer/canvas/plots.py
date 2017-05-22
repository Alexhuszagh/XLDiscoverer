'''
    Gui/Views/Visualizer/Canvas/plots
    _________________________________

    Converts HDF5 leaf data to in-memory arrays for plotting.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import numpy as np

from xldlib.resources.parameters import defaults
from xldlib.utils import decorators
from xldlib.utils.skimage.measure import block_reduce

# load objects/functions
from collections import namedtuple


# OBJECTS
# -------

Plot = namedtuple("Plot", "x y color")
Limit = namedtuple("Limit", "min max")
Pen = namedtuple("Pen", "color width name")

# CONSTANTS
# ---------


COLORS = [
    Pen((0, 0, 225), width=2, name='blue'),
    Pen((255, 0, 0), width=2, name='red'),
    Pen((0, 128, 0), width=2, name='green'),
    Pen((128,0,128), width=2, name='purple'),
    Pen((255,165,0), width=2, name='orange'),
    Pen((255, 255, 225), width=2, name='black'),
]



# HELPERS
# -------


def yield_group(group, indexes):
    '''Yields the (x, y) data for the labels plot'''

    x = group.get_retentiontime()
    y = group.child_intensity()

    if y.size > defaults.DEFAULTS['maximum_plot_points']:
        # interpolation produces much faster plotting
        adjust = int(y.size // defaults.DEFAULTS['maximum_plot_points'])
        y = block_reduce(y, block_size=(1, adjust), func=np.mean)
        x = block_reduce(x, block_size=(adjust,), func=np.mean)

    for index in indexes:
        yi = y[index]
        color = COLORS[index % 6]
        yield Plot(x, yi, color)


@decorators.overloaded
def yield_isotope(group):
    '''Yields the (x, y) data for the isotope plot'''

    index = group.get_charge().index(group)
    x = group.get_retentiontime()
    y = group.intensity()
    color = COLORS[index % 6]
    yield Plot(x, y, color)


# PLOTDATA
# --------


def get_plotdata(group, indexes):
    '''Returns the plot data, including widget colors and labels, as a list'''

    if group.type in {'file', 'labels', 'crosslink', 'charge'}:
        return list(yield_group(group, indexes))
    elif group.type == 'isotope':
        return list(yield_isotope(group, indexes))


# LIMITS
# ------


def get_xlimit(group):
    '''Reutns the x limits for the plot'''

    if group.levels.labels is not None:
        window = group.get_labels().get_window_bounds()
        padding = (window.end - window.start) / 10

        return Limit(window.start - padding, window.end + padding)
    else:
        x = group.get_retentiontime()
        return Limit(x.min(), x.max())


def get_ylimit(group, plotdata, padding=1.2):
    '''Reutns the y limits for the plot'''

    y = (i.y for i in plotdata)
    if group.levels.labels is not None:
        window = group.get_labels().get_window_indexes()
        y = (i[window.start:window.end] for i in y)

    ymax = max(i.max() for i in y)

    return Limit(0, max(100, ymax * padding))
