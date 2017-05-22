'''
    Objects/Documents/Transitions/tools
    ___________________________________

    Memory-mapped data for the transitions document hierarchy and
    structure.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np

from xldlib import exception
from xldlib.resources.parameters import defaults
from xldlib.xlpy import wrappers


# FUNCTIONS
# ---------


def mindiv(a, b):
    '''Normalize value by calculating min of mutual quotients'''

    return min(a/b, b/a)


@wrappers.warnonerror(AssertionError, exception.CODES['014'])
def getglobal(document, vfun=np.vectorize(mindiv)):
    '''Returns whether to search for crosslinked peptide XICs in all files'''

    globalsearch = False
    if defaults.DEFAULTS['quantify_globally']:
        # check to ensure a certain base threshold of gradient similarity
        runtimes = np.array([i.runtime for i in document])
        similarity = vfun(runtimes, runtimes.mean())
        globalsearch = all(
            i > defaults.DEFAULTS['gradient_similarity'] for i in similarity
        )

        assert globalsearch
    return globalsearch
