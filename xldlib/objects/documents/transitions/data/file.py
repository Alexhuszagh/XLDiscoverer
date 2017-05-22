'''
    Objects/Documents/Transitions/Data/file
    _______________________________________

    Memory-mapped data for the transitions file hierarchy and
    structure.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import itertools as it

from xldlib.utils import logger

# load objects/functions
from collections import defaultdict

from .base import repeat, TransitionDataBase
from .labels import TransitionsLabelsData


# DATA
# ----

ROW_DATA = (
    'project',
    'search',
    'runtime',
    'matched',
    'scans',
    'precursor',
    'product'
)


# LEVEL
# -----


@logger.init('document', 'DEBUG')
class TransitionsFileData(TransitionDataBase):
    '''Definitions for the mapping data stores in an input file'''

    # KEYS
    # ----
    _child = TransitionsLabelsData
    _children = 'labels'
    _type = 'file'

    def __init__(self, *args, **kwds):
        super(TransitionsFileData, self).__init__(*args, **kwds)

        index = self.getindex()
        self.cache = self.parent.cache[index]

    #     PUBLIC

    def addfromcrosslink(self, crosslink, data):
        '''Adds a new item to the document from a crosslink'''

        memo = self.memo()
        if crosslink.frozen in memo:
            group = memo[crosslink.frozen]
            group.append_precursors(data, crosslink)
        else:
            memo[crosslink.frozen] = group = self.add_labels()
            group.set_labels(data, crosslink)
        return group

    def add_labels(self, index=None):
        '''Adds a crosslinker labels list to the current file'''

        if index is None:
            index = str(len(self))

        labels = self._child.new(self, index)
        self.append(labels)

        return labels

    #    HIERARCHY

    def get_document(self):
        return self.parent

    def get_file(self):
        return self

    def get_labels(self, labels):
        return self[labels]

    def get_crosslink(self, labels, crosslink):
        return self[labels][crosslink]

    def get_charge(self, labels, crosslink, charge):
        return self[labels][crosslink][charge]

    def get_isotope(self, labels, crosslink, charge, isotope):
        return self[labels][crosslink][charge][isotope]

    def iter_labels(self):
        return iter(self)

    def iter_crosslink(self):
        return it.chain.from_iterable(self)

    def iter_charge(self):
        return repeat(it.chain.from_iterable, 2, self)

    def iter_isotope(self):
        return repeat(it.chain.from_iterable, 3, self)

    #    SPECTRA

    def intensity(self):
        return self.cache.file()[:]

    def child_intensity(self, start=None, end=None):
        return self.get_file().cache.labels()[start:end, :].T

    #    METADATA

    def memo(self):
        return self.parent.memo[self.getindex()]

    #      DATA

    def set_meta(self, row):
        '''Sets the spectral metadata associated with the row'''

        for key in ROW_DATA:
            self.setattr(key, row.data.getattr(key))
        self.setattr('engines', row.data.getattr('engines'))

    #     HELPERS

    def init_cache(self):
        '''Initializes the transitions cache'''

        self.init_isotopes()
        self.init_charges()
        self.init_crosslinks()
        self.init_labels()

    def init_isotopes(self):
        '''Initializes the cache for each of the isotope items'''

        # initialize the data storage
        masses = defaultdict(list)
        for isotope in self.iter_isotope():
            masses[isotope.round()].append(isotope)

        self.cache.init_isotopes(len(masses))

        # set the mass query list
        massorder = sorted(masses)
        self.setattr('massorder', massorder)
        for index, mass in enumerate(massorder):
            for isotope in masses[mass]:
                isotope.setattr('isotope_index', index)

    def init_charges(self):
        '''Initializes the cache for each of the charge items'''

        charges = list(self.iter_charge())
        dimensions = len(charges)
        self.cache.init_charges(dimensions)
        for index, charge in enumerate(charges):
            charge.setattr('charge_index', index)

    def init_crosslinks(self):
        '''Initializes the cache for each of the crosslink items'''

        crosslinks = list(self.iter_crosslink())
        dimensions = len(crosslinks)
        self.cache.init_crosslinks(dimensions)
        for index, crosslink in enumerate(crosslinks):
            crosslink.setattr('crosslink_index', index)

    def init_labels(self):
        '''Initializes the cache for each of the labels items'''

        labels = list(self.iter_labels())
        dimensions = len(labels)
        self.cache.init_labels(dimensions)
        for index, label in enumerate(labels):
            label.setattr('labels_index', index)
