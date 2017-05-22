'''
    General/Mapping/recursive
    _________________________

    Recursive defaultdict recipes which use themselves as factories.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import defaultdict

__all__ = [
    'recursive_dict',
    'RecursiveDict'
]


# FUNCTIONS
# ---------


def recursive_dict():
    '''Function constructor for a recursive defaultdict'''

    return defaultdict(recursive_dict)


# EXTENSIBLE
# ----------


class RecursiveDict(defaultdict):
    '''Inheritable recipe for a recursive dictionary, allowing subclassing'''

    def __init__(self, *args, **kwargs):
        super(RecursiveDict, self).__init__(RecursiveDict, *args, **kwargs)
