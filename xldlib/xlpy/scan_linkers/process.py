'''
    XlPy/Scan_Linkers/process
    _________________________

    Handler for a multiprocessing example with a pool map.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import numpy as np


# PARALLELIZATION
# ---------------


def matchingprecursor(precursor_mz, ppmthreshold, mz):
    '''Checks if the precursor_mz is in the m/z list within the threshold'''

    ppm = abs(mz - precursor_mz) / precursor_mz
    indexes, = np.where(ppm < ppmthreshold)
    return bool(indexes.size)
