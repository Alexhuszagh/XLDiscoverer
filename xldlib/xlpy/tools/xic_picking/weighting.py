'''
    XlPy/Tools/Xic_Picking/weighting
    ________________________________

    Tools to weight peak-picking algorithms by biophysical properties,
    such as correlations between different isotope patterns.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np

from xldlib.definitions import ZIP
from xldlib.utils import logger
from xldlib.utils.xictools import scoring


# CORRELATIONS
# ------------


def get_cluster_dotps(clusters):
    return np.array([cluster.get_dotps() for cluster in clusters])


def get_cluster_correlation(clusters):
    return np.array([cluster.get_masscorrelations() for cluster in clusters])


# EUCLIDEAN DISTANCE
# ------------------


def get_nonoverlapping_distances(clusters):
    '''Returns the euclidean distance from each anchor to the cluster'''

    distances = []
    for cluster in clusters:
        distances.append(list(cluster.yield_distance()))

    # need to Tranpose so it is by anchor and not by cluster
    return np.array(distances).T


# WEIGHTING
# ---------


@logger.call('peakpicking', 'debug')
def get_isotope_weight(clusters, dotp_weight=0.35, size_weight=0.2,
    mass_weight=0.45, **kwds):
    '''
    Returns a weighted matrix for each isotope cluster
    '''

    # calculate our size, dotp and mass_correlation coefficients
    weights = (scoring.get_size_weight(i.start, i.end) for i in clusters)
    size = np.fromiter(weights, dtype=int)

    # tranpose since we want grouped by cluster, not by charge
    dotp = get_cluster_dotps(clusters).T
    mass = get_cluster_correlation(clusters).T

    return (size*size_weight) + (dotp*dotp_weight) + (mass*mass_weight)


@logger.call('peakpicking', 'debug')
def get_anchor_weight(clusters):
    '''
    Weights all the anchor points using a nearest non-overlapping
    feature approach (1D).
    If the element overlaps, the value is 1.
    If the element does not overlap but is the nearest, then the value is 2.
        The returned weight is 1 / sqrt(value)
    '''

    # get the euclidean distances sorted
    distance_matrix = get_nonoverlapping_distances(clusters)
    sortedargs = np.argsort(distance_matrix)

    # weight each distance
    weight_matrix = np.zeros(sortedargs.shape)
    zipped = ZIP(sortedargs, distance_matrix)
    for row, (indexes, distances) in enumerate(zipped):

        counter = 2
        for index in indexes:
            if distances[index] == 0:
                weight_matrix[row][index] = 1
            else:
                weight_matrix[row][index] = counter
                counter += 1

    return np.prod((1 / np.sqrt(weight_matrix)), axis=0)
