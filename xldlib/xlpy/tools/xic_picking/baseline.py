'''
    XlPy/Tools/Xic_Picking/baseline
    _______________________________

    Tools to calculate and normalize the XIC baseline.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np


# FUNCTIONS
# ---------


def calculate_baseline(y):
    return np.median(y)


def calculate_noise(y):
    return np.std(y)
