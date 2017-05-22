'''
    Utils/math_
    ___________

    Numerical operations on array, avoiding nonfinite float
    propogation, and statistical analysis oeprations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .array import finite, spacing, to_num
from .functions import gaussian
from .gaussian import fit_gaussian
from .number import equal, isinf, isnan, isnull
from .stats import sheppards, normalized_angle_sqrt, normalized_edge_dotp

__all__ = [
    'array',
    'functions',
    'gaussian',
    'number',
    'stats'
]
