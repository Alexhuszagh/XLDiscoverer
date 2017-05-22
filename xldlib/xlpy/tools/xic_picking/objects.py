'''
    XlPy/Tools/Xic_Picking/objects
    ______________________________

    Object definitions for XIC peak picking.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load objects/functions
from collections import namedtuple

# OBJECTS
# -------

Bounds = namedtuple("Bounds", "start end")


class WeightedXicBounds(namedtuple("WeightedXicBounds", "start end score")):
    '''Subclass with classmethods for initializing'''

    @classmethod
    def fromcluster(cls, cluster, score):
        return cls(cluster.start, cluster.end, score)
