'''
    Onstart/registers
    _________________

    ABC registers for various complex types.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numbers

import numpy as np

# REGISTERS
# ---------

numbers.Integral.register(np.integer)
