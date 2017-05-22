'''
    General/Mapping/hashable
    ________________________

    Hashable (immutable) mapping data object definitions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import abc

from collections import Mapping

__all__ = [
    'HashableMapping',
    'HashableDict'
]


# HASH
# ----


class HashableMapping(Mapping):
    '''
    Immutable Mapping object with blocked setters/deleters,
    and implements a hash function.
    '''

    __metaclass__ = abc.ABCMeta

    #      MAGIC

    def __hash__(self):
        '''Hash generator from immutable, sorted items'''

        return hash(tuple(sorted(self.items())))

    #    PROPERTIES

    @property
    def blocked(self):
        raise NotImplementedError

    __delitem__ = __setitem__ = clear = update = blocked
    pop = popitem = setdefault = blocked


class HashableDict(HashableMapping, dict):
    '''Concrete implementation of the HashableMapping ABC'''

    def __getitem__(self, key, dict_getitem=dict.__getitem__):
        '''
        Override ABC method to provide item lookups.
        Equivalent to self[key]
        '''

        return dict_getitem(self, key)
