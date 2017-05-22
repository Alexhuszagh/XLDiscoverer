'''
    Objects/Run/dataset
    ___________________

    Runtime parameters for main thread, which can be reconstructed
    from the run dataset.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import six
import weakref

import numpy as np

from .. import pytables
from xldlib.resources import paths
from xldlib.utils import logger

# load objects/functions
from collections import namedtuple

# CONSTANTS
# ---------

MS1KEY = 'ms1'


# DATA
# ----

SPECTRA = dict(where='/', name='spectra', title='Raw Spectral Data')


# OBJECTS
# -------

SpectralWindow = namedtuple("SpectralWindow", "mz intensity")


@logger.init('scans', level='DEBUG')
class Scan(pytables.Group):
    '''Definitions for a single scan object'''

    def __init__(self, parent, group, **kwds):
        super(Scan, self).__init__()

        self.parent = parent
        self.group = group

        for key, value in kwds.items():
            self.setattr(key, value)
        for key, value in self.group._v_leaves.iteritems():
            setattr(self, key, value)

        self.setweakrefs()

    #      SETTERS

    def setweakrefs(self):
        self.scanlevel = weakref.ref(self.parent)
        self.file = weakref.ref(self.scanlevel().parent)
        self.spectra = weakref.ref(self.file().parent)
        self.document = weakref.ref(self.spectra().parent)

    #      GETTERS

    def getrt(self):
        if self.hasattr('precursor_rt'):
            return self.getattr('precursor_rt')
        else:
            return self.getattr('retention_time')

    #      PUBLIC

    def newarray(self, key, array):
        array = self.create_array(key, obj=array)
        array.flush()
        setattr(self, key, array)
        return array

    def todict(self):
        '''Returns a dictionary representation of the current metadata'''

        return {
            'precursor_num': self.getattr('num'),
            'precursor_rt': self.getrt(),
            'precursor_mz': self.getattr('precursor_mz'),
            'precursor_z': self.getattr('precursor_z'),
        }

    def masswindow(self, window):
        '''Returns a mass window from the mz array'''

        mz = self.mz[:]
        indexes = np.where((mz > window.min) & (mz < window.max))
        return SpectralWindow(mz[indexes], self.intensity[indexes])


@logger.init('scans', level='DEBUG')
class ScanLevel(pytables.Group):
    '''Definitions for the spectral group parent of a series of scans'''

    # PYTABLES PARAMETERS
    # -------------------
    maxgroups = 10000       # PyTables default, 16384

    def __init__(self, parent, group):
        super(ScanLevel, self).__init__()

        self.parent = parent
        self.group = group

        self.setweakrefs()
        self.setparameters()

    #      SETTERS

    def setweakrefs(self):
        self.file = weakref.ref(self.parent)
        self.spectra = weakref.ref(self.file().parent)
        self.document = weakref.ref(self.spectra().parent)

    def setparameters(self, steps=None):
        if steps is None:
            from xldlib.resources.parameters import defaults
            steps = defaults.DEFAULTS['precursor_scan_steps']
        self._steps = steps

    def setscans(self):
        self.scans = np.sort(np.array(list(self)).astype(int))[::-1]

    #      GETTERS

    def getscan(self, key):
        if not isinstance(key, six.string_types):
            key = str(key)
        return Scan(self, self[key])

    #      HELPERS

    @pytables.silence_tbperformance
    def newscan(self, num, title='Scan holder for scan {}', **kwds):
        '''Adds a new scan binds all keywords as Attributes'''

        group = self.create_group(str(num), title=title.format(num))
        return Scan(self, group, num=num, **kwds)

    def findscan(self, num):
        '''Finds all possible sequential scans from the current product scan'''

        if not hasattr(self, "scans"):
            self.setscans()

        bool_ = (self.scans < num) & (num - self.scans < self._steps)
        nums = self.scans[np.where(bool_)[0]]
        for index, num in enumerate(nums):
            if index == 0 or previous - num == 1:
                previous = num
                yield num

    def isprecursor(self):
        return self.group._v_name == 'precursor'

    def isproduct(self):
        return self.group._v_name == 'product'

    #      ITER

    def keys(self, ignore=()):
        for key in self:
            if key not in ignore:
                yield key

    def values(self, ignore=()):
        for key in self.keys(ignore):
            yield self.getscan(key)

    def items(self, ignore=()):
        for key in self.keys(ignore):
            yield key, self.getscan(key)

    def get(self, key, default=None):
        if self.hasgroup(key):
            return self.getscan(key)
        return default


@logger.init('scans', level='DEBUG')
class FileRow(pytables.Group):
    '''Definitions for a file row of the HDF5 group'''

    # KEYS
    # ----
    ms1 = MS1KEY

    def __init__(self, parent, group, **kwds):
        super(FileRow, self).__init__()

        self.parent = parent
        self.group = group

        self.setweakrefs()
        if kwds.get('new'):
            self.new()

    #      PUBLIC

    @logger.call('scans', level='DEBUG')
    def new(self):
        '''Initializes a new FileRow'''

        for key in self.document().keys():
            title = 'Spectral data for {} scans'.format(key)
            self.create_group(key, title)

    #      GETTERS

    def getgroup(self, key):
        return ScanLevel(self, self[key])

    #      SETTERS

    def setweakrefs(self):
        self.spectra = weakref.ref(self.parent)
        self.document = weakref.ref(self.spectra().parent)

    #      HELPERS

    def delevel(self):
        '''Dependent import to avoid conflicting with multiprocessing'''

        from . import delevel
        delevel.delevel(self)

    def newgroup(self, key, title='Spectral data for {}'):
        '''Creates and returns a new group from a given key'''

        document = self.document()
        if not (key == 'ms1' and not document.quantitative):
            return ScanLevel(self, self.create_group(key, title.format(key)))

    def keys(self, ignore=(), mode=None):
        '''FR.keys() -> iter(('ms1', 'precursor', 'product'))'''

        document = self.document()
        if mode is None:
            mode = document.mode

        for key in document.keys(mode):
            if key not in ignore:
                yield key

    def values(self, ignore=(), mode=None):
        for key in self.keys(ignore, mode):
            yield self.getgroup(key)

    def items(self, ignore=(), mode=None):
        for key in self.keys(ignore, mode):
            yield key, self.getgroup(key)

    def get(self, key, default=None):
        if self.hasgroup(key):
            return self.getgroup(key)
        return default


@logger.init('scans', level='DEBUG')
class Spectra(pytables.Group):
    '''Methods for a spectral holder'''

    def __init__(self, parent, group):
        super(Spectra, self).__init__()

        self.parent = parent
        self.group = group

        self.setweakrefs()

    #      PUBLIC

    def addrow(self, row=None):
        '''Adds a new row to the current spectral object'''

        if row is None:
            row = len(self.group._v_groups)

        group = self.create_group(str(row), title='File row {}'.format(row))
        return FileRow(self, group, new=True)

    #      SETTERS

    def setweakrefs(self):
        self.document = weakref.ref(self.parent)

    #      GETTERS

    def getfilerow(self, row):
        '''Returns the raw file row HDF5 group'''

        assert int(row) < len(self)
        return FileRow(self, self[str(row)])


# DATASET
# -------


@logger.init('scans', level='DEBUG')
class RunDataset(pytables.Root):
    '''Provides a storage backend for the XL Discoverer runtime thread.'''

    # KEYS
    # ----
    _keys = {
        0: ['precursor', 'product'],
        1: ['scans']
    }

    def __init__(self, quantitative, path=None, **kwds):
        super(RunDataset, self).__init__()

        self.quantitative = quantitative
        self.table = None
        self.spectra = None
        self.mode = None

        if path is not None:
            self.open(path, kwds.pop('mode', 'a'))
        elif kwds.pop('new', False):
            self.new()

    def __iter__(self):
        '''Returns an iterator for all of the spectra'''

        raise NotImplementedError

    #      I/O

    @logger.call('scans')
    def new(self, path=None):
        '''Initializes the Pytables file and creates the main table'''

        path = self.__get_path(path)
        self._new(path)
        self.spectra = Spectra(self, self.file.create_group(**SPECTRA))

    @logger.call('scans')
    def open(self, path, mode='a'):
        '''Opens a pre-existing file object'''

        self._open(path, mode=mode)
        self.spectra = Spectra(self, self.root.spectra)

    @logger.call('scans')
    def close(self):
        '''Closes an open file object'''

        self._close()
        self.spectra = None

    @staticmethod
    def __get_path(path):
        '''Returns a valid path object, which defaults to the current db'''

        if path is None:
            path = paths.FILES['spectra']
        return path

    #     HELPERS

    def deleterows(self, rows):
        '''
        Deletes the given rows from the file and then reindexes the
        remaining values
        '''

        for row in rows:
            group = self.spectra.getfilerow(row)
            group.remove(recursive=True)

        length = len(self) - len(rows)
        self.setattr('length', length)

        self.reindex()

    def keys(self, mode=None):
        if mode is None:
            mode = self.mode

        if getattr(self, "quantitative", False) and not mode:
            return iter(self._keys[mode] + [MS1KEY])
        else:
            return iter(self._keys[mode])

    def reindex(self):
        '''Reindexes the spectral holder'''

        groups = self.file.root.spectra._v_groups
        children = sorted(groups, key=int)

        for index, groupname in enumerate(children):
            newname = str(index)
            if newname != groupname:
                groups[groupname]._f_move(newname=newname)
