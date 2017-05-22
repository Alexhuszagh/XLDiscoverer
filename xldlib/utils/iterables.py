'''
    Utils/iterables
    _______________

    Modifications of itertools functions to filter for desired behavior
    cheaply.
'''

# load modules
import itertools as it

import numpy as np


# CARTESIAN PRODUCTS
# ------------------


def num_product(*args, **kwds):
    '''
    product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
    product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111

    Adds in feature with min_ and max_ for summed list for integer products.
    '''

    generator = it.product(*args, repeat=kwds.get('repeat', 1))
    min_ = kwds.get('min', -1)
    max_ = kwds.get('max', np.inf)
    for prod in generator:
        if min_ <= sum(prod) <= max_:
            yield tuple(prod)


def mod_product(*args, **kwds):
    '''
    product([1, 2], [2, 3]) --> (1, 2), (2, 3), (1, 3)

    Considers all iterable products as long without element repition,
    for mod products from given indexes
    '''

    generator = it.product(*args, repeat=kwds.get('repeat', 1))
    for prod in generator:
        # faster than counter conversion or sorting
        flattened = [i for item in prod for i in item]
        unique = len(flattened) == len(set(flattened))
        if unique:
            yield tuple(prod)

