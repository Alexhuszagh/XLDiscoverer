'''
    XlPy/Tools/Xic_Picking/picking
    ______________________________

    Tools to pick peaks from an extracted ion chromatogram.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np

# load objects/functions
from collections import namedtuple

# OBJECTS
# -------
Intersect = namedtuple("Intersect", "above up down")


class Cluster(namedtuple("Cluster", "xicfit start end")):
    '''Subclass with bound methods for facile data processing and scoring'''

    #    YIELDERS

    def yield_distance(self):
        '''Returns the euclidean distance from each anchor to the cluster'''

        x = self.get_x()
        min_ = x.min()
        max_ = x.max()

        for anchor in self.xicfit.anchors:
            # add the minimum distance from the anchor to the cluster
            if min_ < anchor < max_:
                yield 0
            elif anchor > max_:
                yield anchor - max_
            elif anchor < min_:
                yield min_ - anchor

    #    GETTERS

    def get_x(self):
        return self.xicfit.x[self.start:self.end]

    def get_y(self):
        return self.xicfit.y[self.start:self.end]

    def get_dotp(self, index):
        return self.xicfit.get_meandotp(index, self.start, self.end)

    def get_dotps(self):
        return [self.get_dotp(i) for i in range(len(self.xicfit.isotopes))]

    def get_masscorrelation(self, index):
        return self.xicfit.get_masscorrelation(index, self.start, self.end)

    def get_masscorrelations(self):
        return [self.get_masscorrelation(i) for i in
            range(len(self.xicfit.isotopes))]


# CLUSTERING
# ----------


def pad_clusters(length, *clusters):
    '''Adds padding to each of the clusters'''

    for cluster in clusters:
        min_ = cluster.min()
        max_ = cluster.max()
        if min_ != 0 and max_ < length - 1:
            yield np.r_[min_ - 1, cluster, max_ + 1]
        elif min_ != 0:
            yield np.r_[min_ - 1, cluster]
        elif max_ < length - 1:
            yield np.r_[cluster, max_ + 1]
        else:
            yield cluster


# INTERSECTIONS
# -------------


def getintersect(xicfit, valley=0.25, stddev=3, **kwds):
    '''Returns the intersection indexes as a namedtuple'''

    # get our two possible baselines
    valley_level = xicfit.y.max() * valley
    signal_to_noise = xicfit.baseline + stddev * xicfit.noise

    # grab the minimum threshold, and find our intersections with the valley
    threshold = min(valley_level, signal_to_noise)
    above = xicfit.y > threshold
    up, = np.where(above[1:] & ~above[:-1])
    down, = np.where(~above[1:] & above[:-1])

    return Intersect(above, up, down)


def splitvalley(xicfit, intersect):
    '''Splits the array into series that are >= y.max() * valley'''

    indexes, = np.where(intersect.above)
    clusters = np.split(indexes, np.argwhere(np.diff(np.r_[0, indexes]) > 1))
    filtered = (i for i in clusters if i.size > 0)
    padded = pad_clusters(xicfit.y.size, *filtered)

    for cluster in padded:
        yield Cluster(xicfit, cluster.min(), cluster.max())


# EXTREMA
# -------


def get_localminima(y, minimum=0, maximum=float("inf")):
    '''Returns the local minima from the xicfit parameters'''

    left = np.r_[True, y[1:] < y[:-1]]
    right = np.r_[y[:-1] < y[1:], True]
    # include absolute minima, which will break this
    is_min = y == minimum
    is_max = y < maximum

    return np.where((left & right & is_max) | is_min)[0]
