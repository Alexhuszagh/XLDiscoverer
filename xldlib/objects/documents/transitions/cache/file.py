'''
    Objects/Documents/Transitions/Cache/file
    ________________________________________

    HDF5 data cache for an individual HDF5 file.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import tables as tb

from xldlib.objects import pytables
from xldlib.utils import logger

# load objects/functions
from .save import copy_group, IO_ROWS


# CONSTANTS
# ---------

FILE_ARRAYS = (
    ('retentiontime', 'Retentiontime values'),
    ('file', 'File intensity values')
)

ISOTOPE_ARRAYS = (
    ('intensity', 'Isotope intensity values'),
    ('mz', 'Isotope m/z values'),
)


# DIMENSIONS
# ----------

# Expected scans per file, undershot to avoid excessive I/O
EXPECTED_ROWS = 2 * IO_ROWS
# Column chunking with rows to make 1 mb chunk, overshot slightly
EXPECTED_COLUMNS = 10


# FILE
# ----


@logger.init('document', 'DEBUG')
class TransitionsFileCache(pytables.Group):
    '''Definitions for the spectral table from an input row'''

    def __init__(self, document, row=None):
        super(TransitionsFileCache, self).__init__()

        self.document = document
        self.root = self.document.file.root

        if row is not None:
            self.checknew(row)

    #     PUBLIC

    @pytables.silence_naturalname
    def new(self, row):
        '''Initializes a new Pytables files group'''

        self.group = self.document.file.create_group('/',
            name=str(row),
            title='File data',
            filters=self.document.filter)

        for name, title in FILE_ARRAYS:
            self.create_earray(
                name=name,
                title=title,
                atom=tb.Float64Atom(),
                shape=(0,),
                expectedrows=EXPECTED_ROWS,
                chunkshape=(EXPECTED_ROWS,))

    def open(self, row):
        self.group = getattr(self.root, str(row))

    def checknew(self, row):
        '''Checks if the object exists, creates if it doesn't'''

        if hasattr(self.root, str(row)):
            self.open(row)
        else:
            self.new(row)

    def copy(self, *args, **kwds):
        return copy_group(self.group, *args, **kwds)

    #   INITIALIZERS

    def init_isotopes(self, dimensions):
        '''Initializes the array for the isotope values'''

        for name, title in ISOTOPE_ARRAYS:
            self.create_earray(name=name,
                title=title,
                atom=tb.Float64Atom(),
                shape=(0, dimensions),
                expectedrows=EXPECTED_ROWS,
                chunkshape=(EXPECTED_ROWS, 10))

    def init_charges(self, dimensions):
        '''Initializes the array for the isotope values'''

        self.create_earray(name='charge',
            title='Charge intensity values',
            atom=tb.Float64Atom(),
            shape=(0, dimensions),
            expectedrows=EXPECTED_ROWS,
            chunkshape=(EXPECTED_ROWS, 10))

    def init_crosslinks(self, dimensions):
        '''Initializes the array for the isotope values'''

        self.create_earray(name='crosslink',
            title='Crosslink intensity values',
            atom=tb.Float64Atom(),
            shape=(0, dimensions),
            expectedrows=EXPECTED_ROWS,
            chunkshape=(EXPECTED_ROWS, 10))

    def init_labels(self, dimensions):
        '''Initializes the array for the isotope values'''

        # no chunkshape, are read sequentially
        self.create_earray(name='labels',
            title='Label intensity values',
            atom=tb.Float64Atom(),
            shape=(0, dimensions),
            expectedrows=EXPECTED_ROWS)

    #   ATTRIBUTES

    def retentiontime(self):
        return self.group.retentiontime

    def mz(self):
        return getattr(self.group, 'mz', None)

    def intensity(self):
        return getattr(self.group, 'intensity', None)

    def charge(self):
        return getattr(self.group, 'charge', None)

    def crosslink(self):
        return getattr(self.group, 'crosslink', None)

    def labels(self):
        return getattr(self.group, 'labels', None)

    def file(self):
        return getattr(self.group, 'file', None)
