'''
    Objects/Documents/Transitions/Data/base
    _______________________________________

    Inheritable definitions for a memory-mapped file structure.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import operator as op
import six

from collections import namedtuple

from xldlib.general import mapping, sequence
from xldlib.objects import mappedfile
from xldlib.utils import logger, serialization, xictools


# CONSTANTS
# ---------

PARENT = op.attrgetter('parent')


# HELPERS
# -------


def repeat(f, n, x):
    '''Repeat a function (f) call (n) times with arg(s) (x)'''

    if n == 0:
        return x
    else:
        return f(repeat(f, n-1, x))


# OBJECTS
# -------

LinearRange = namedtuple("LinearRange", "start end")



@sequence.serializable('TransitionLevels')
class Levels(namedtuple("Levels", "file labels crosslink charge isotope")):
    '''Levels definition with defaults of none for all values'''

    @logger.call('document', 'debug')
    def __new__(cls, file=None, labels=None, crosslink=None,
        charge=None, isotope=None):
        return super(Levels, cls).__new__(
            cls, file, labels, crosslink, charge, isotope)


# OBJECTS
# -------


@logger.init('document', 'DEBUG')
@serialization.register('TransitionDataBase')
class TransitionDataBase(mappedfile.Data):
    '''Definitions for a transitions object'''

    def __init__(self, parent, level, data=None):
        super(TransitionDataBase, self).__init__()

        self.parent = parent
        self.data = data

        self.children = self.data.get(self._children, ())
        self.set_levels(level)

    #     MAGIC

    def __iter__(self):
        for index, item in enumerate(self.children):
            key = self.get_key(index)
            yield self._child(self, key, item)

    def __getitem__(self, item):
        '''Provides key-based or index-based lookups using a mapped dict'''

        if isinstance(item, six.string_types):
            key = item
            index = self.get_index(key)
        else:
            index = item
            key = self.get_key(index)

        item = self.children[index]
        return self._child(self, key, item)

    def __len__(self):
        if self.children is not None:
            return len(self.children)
        else:
            # NoneType // isotope child
            return 0

    def __eq__(self, other):
        return self.data == other.data

    def __json__(self):
        return {
            '__data__': self.data,
            '__builtin__': 'dict'
        }

    #  CLASS METHODS

    @classmethod
    def new(cls, parent, level):
        '''Class constructor for new item levels'''

        #levels = getattr(parent, "levels", Levels())

        # levels definitions
        data = {
            'attrs': {
                'type': cls._type,
                'level': level
            }
        }

        # checkstate
        if cls._type in {'crosslink', 'charge', 'isotope'}:
            data['attrs']['checked'] = True

        # children
        if hasattr(cls, "_children"):
            data[cls._children] = []
            data['lookup'] = mapping.BidirectionalDict()

        return cls(parent, level, data)

    #     PUBLIC

    #   ATTRIBUTES

    def setattr(self, attr, value, recurse=False):
        '''Attribute writer, with an optional recursion flag for children'''

        self.data['attrs'][attr] = value
        if recurse:
            for item in self:
                item.setattr(attr, value, recurse=True)

    def getindex(self):
        return getattr(self.levels, self._type)

    #    SEQUENCE

    def set_levels(self, level):
        '''Sets the hierarchical order (dynamically) for the object'''

        if not hasattr(self.parent, "levels"):
            self.levels = Levels(**{self._type: level})
        else:
            self.levels = self.parent.levels._replace(**{self._type: level})

    def append(self, item):
        '''Appends an item to the children list'''

        self.children.append(item.data)
        self.children.sort(key=self._sort)

        lookup = {j['attrs']['level']: i for i, j in enumerate(self.children)}
        self.data['lookup'] = mapping.BidirectionalDict(lookup)

    def index(self, item):
        '''Indexes the child group within self._v_groups'''

        for index, child in enumerate(self):
            if item == child:
                return index

        raise IndexError("Item not in " + self.__class__.__name__)

    #      SPECTRA

    def get_retentiontime(self, start=None, end=None, force_load=False):
        '''Returns a memory mapped if possible, load from cache otherwise'''

        if all((not force_load,
                self.get_document().memory,
                self.levels.labels)):
            return self.get_labels().mem_rt[start:end]
        else:
            return self.get_file().cache.retentiontime()[start:end]

    def area(self):
        return xictools.get_integral(self)

    def ymax(self):
        return max(self.intensity())

    #     HELPERS

    def get_key(self, index):
        return self.data['lookup'].reverse.get(index)
        #return self.data.get('lookup', mapping.BidirectionalDict()).reverse.get(index)

    def get_index(self, key):
        return self.data.get('lookup', {}).get(key)

    def has_index(self, index):
        return index in self.data['lookup'].reverse
        #return index in self.data.get('lookup', mapping.BidirectionalDict()).reverse

    def has_key(self, index):
        return index in self.data.get('lookup', {})

    def _sort(self, item):
        return int(item['attrs']['level'])
