'''
    XlPy/Tools/Xic_Picking/abd3d
    ____________________________

    Modified implementation of the AB3D algorithm for robust
    fitting of extracted ion chromatograms, which was originally
    developed by Aoshima, et al.
        DOI: 10.1186/s12859-014-0376-0

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import operator as op

import numpy as np

from . import objects, picking, weighting


# VALLEY
# ------


def get_best_abovevalley(xicfit, intersect, **kwds):
    '''
    Returns the best above the valley threshold as a (start, end) pair
    This finds all the clusters above a certain valley threshold, then
    weights each according to size, dot product, and correlation
    to a theoretical isotope pattern using a pearson correlation.
    '''

    # get our clustering and parameters
    clusters = list(picking.splitvalley(xicfit, intersect))

    # calculate the weighting
    isotopes = weighting.get_isotope_weight(clusters, **kwds)
    anchors = weighting.get_anchor_weight(clusters)
    weighted = isotopes * anchors

    # get the maximum value from our weighting
    if not weighted.size:
        return None
    else:
        index = np.unravel_index(np.argmax(weighted), weighted.shape)[1]
        return clusters[index]


# UNDULATIONS
# -----------


def sample_undulations(cluster, intersect, max_undulations=2, **kwds):
    '''Returns a sample set of start and end combinations'''

    left_indexes, = np.where(intersect.up < cluster.start)
    right_indexes, = np.where(intersect.down > cluster.end)

    left = intersect.up[left_indexes[::-1][:max_undulations]]
    left = np.r_[cluster.start, left]

    right = intersect.down[right_indexes[:max_undulations]]
    right = np.r_[cluster.end, right]

    for left_index, start in enumerate(left):
        for right_index, end in enumerate(right):
            undulations = left_index + right_index
            if undulations <= max_undulations:
                yield cluster._replace(start=start, end=end)


def weight_cluster(cluster, dotp_weight=0.35, size_weight=0.2,
    mass_weight=0.45, **kwds):
    '''
    Weights the resulting boundss, favoring longer
    boundss if possible with a moderate weight
    '''

    size = (cluster.end - cluster.start + 1) / cluster.xicfit.y.size

    dotp = max(cluster.get_dotps())
    mass = max(cluster.get_masscorrelations())

    return (size*size_weight) + (dotp*dotp_weight) + (mass*mass_weight)


def get_best_undulation(undulations, **kwds):
    '''Returns the best scoring undulation based on span and dot product'''

    scores = []
    for cluster in undulations:
        scores.append(weight_cluster(cluster, **kwds))

    index, score = max(enumerate(scores), key=op.itemgetter(1))
    return objects.WeightedXicBounds.fromcluster(undulations[index], score)


# BOUNDING
# --------


def get_localminima_bounds(bounds, y):
    '''
    Returns the start and end positions from the acquiried local minima
    after finding the best theoretical undulation, which is supplied.
    '''

    localmin = picking.get_localminima(y)

    # grab the start position, which should be less than the valley bounds
    # or the valley bounds
    start = np.r_[0, localmin[np.where(localmin < bounds.start)]][-1]
    if y[start] > y[bounds.start]:
        start = bounds.start

    last_index = y.size - 1
    end = np.r_[localmin[np.where(localmin > bounds.end)], last_index][0]
    if y[end] > y[bounds.end]:
        end = bounds.end

    return objects.WeightedXicBounds(start, end, bounds.score)


def boundab3d(xicfit, **kwds):
    '''
    Fast algorithm which has been modified from the original implementation
    to include the dot product between isotopic patterns to validate
    the original AB3D selection.

    AB3D is named for using 3D data, ie, m/z, intensity and retention
    time, and we add another dimension (isotopic correlation) to
    improve the XIC fitting.
    '''

    intersect = picking.getintersect(xicfit, **kwds)
    valley_cluster = get_best_abovevalley(xicfit, intersect, **kwds)
    if valley_cluster is None:
        # null bounds
        return objects.WeightedXicBounds(0, xicfit.x.size -1, 0)

    undulations = list(sample_undulations(valley_cluster, intersect, **kwds))
    undulation_bounds = get_best_undulation(undulations, **kwds)

    return get_localminima_bounds(undulation_bounds, xicfit.y)
