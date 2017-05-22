'''
    General/Mapping/reverse
    _______________________

    Mapping object with forward and reverse lookups, providing O(1)
    time performance for both key and value lookups.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import functions


__all__ = [
    'BidirectionalDict'
]


# BIDIRECTIONAL
# -------------


@functions.serializable('Bidirectional')
class BidirectionalDict(dict):
    '''
    Dictionary storing key-value pairs redundantly as
    value-key pairs. Standard __getitem__ performs the
    forward lookup, __call__ performs the reverse lookup,
    similar to an `Enum`.
    '''

    def __init__(self, *args, **kwds):
        super(BidirectionalDict, self).__init__()

        self._reverse = {}
        if args or kwds:
            self.update(*args, **kwds)

    #   PROPERTIES

    @property
    def reverse(self):
        return self._reverse

    def __setitem__(self, key, value, dict_setitem=dict.__setitem__):
        '''
        Set key-value pair and redundantly store inverse.

        Args:
            key (hashable):   forward lookup
            value (hashable): reverse lookup
        '''

        dict_setitem(self, key, value)
        self.reverse[value] = key

    def __delitem__(self, key, dict_delitem=dict.__delitem__):
        '''
        Delete value from inverse mapping, then remove key from self.

        Args:
            key (str):      forward lookup
        '''

        del self.reverse[self[key]]
        dict_delitem(self, key)

    def __call__(self, value):
        '''
        Find key from value using reverse lookup.

        Args:
            value (hashable): reverse lookup
        '''

        return self.reverse[value]

    #     PUBLIC

    update = functions.update_setitem

    def clear(self):
        '''Clear both self and the reverse lookup'''

        super(BidirectionalDict, self).clear()
        self._reverse.clear()

    def pop(self, key, *args):
        '''
        Remove key and return value to user, updating both lookups.

        Args:
            key (hashable): forward lookup
        '''

        try:
            value = self[key]
            del self[key]
            return value

        except KeyError:
            if not args:
                raise KeyError
            else:
                return args[0]

    def popitem(self):
        '''Pop random key and return value to user, updating both lookups.'''

        key, value = super(BidirectionalDict, self).popitem()
        del self.reverse[value]

        return (key, value)

    def setdefault(self, key, default=None):
        '''
        Set key to default and return default if key not previously
        defined, else, return self[key].

        Args:
            key (hashable):     forward lookup
            default (hashable): default value if key not set
        '''

        if key not in self:
            self[key] = default
            return default
        return self[key]
