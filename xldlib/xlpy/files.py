'''
    XlPy/files
    __________

    Processing functions for individual rows for XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import operator as op
import os
import weakref

from xldlib import exception
from xldlib.onstart.main import APP
from xldlib.qt.objects import base
from xldlib.resources.parameters import input_files
from xldlib.utils import logger
from xldlib.utils.io_ import ziptools
from xldlib.xlpy import matched, scan_linkers, wrappers

# load objects/functions
from xldlib.definitions import partial


# HELPERS
# -------


def getmatcher(key):
    '''Wrapper for matching objects'''

    source = APP.discovererthread
    if key == 'matched':
        return source.parameters.search
    else:
        return source.parameters.spectra


# ROWS
# ----


@logger.init('xlpy', 'DEBUG')
class FileRow(base.BaseObject):
    '''Definitions for individual files'''

    def __init__(self, parent, files):
        super(FileRow, self).__init__()

        self.parent = weakref.ref(parent)
        self.files = files
        self.engines = {}
        self.index = len(parent)

        self.source = weakref.proxy(self.app.discovererthread)
        self.data = self.source.matched.newtable(files)
        self.spectra = self.source.rundata.spectra.addrow()
        self.linked = scan_linkers.Row(self)

        if self.source.quantitative:
            self.transitions = self.source.transitions.addrow()

    #      PUBLIC

    def delete(self):
        '''Cleans up the HDF5 storage and objects bound to the '''

        self.source.matched.delete(self.index)
        self.spectra.remove(recursive=True)
        if self.source.quantitative:
            self.transitions.remove(recursive=True)

    def reindex(self, index):
        '''Adjusts the current row to use the new indexer'''

        self.index = index
        self.spectra.rename(str(index))
        if self.source.quantitative:
            self.transitions.rename(str(index))

    def update(self):
        '''Updates the current FileRow after spectral parsing'''

        if self.source.quantitative:
            self.transitions.set_meta(self)

    def checkfile(self):
        assert all(os.path.exists(i) for i in self.files.values())

    def unzipfiles(self):
        '''Unzips the target files to store the unzipped file on disk'''

        for key, path in self.files.items():
            decompressed = ziptools.decompress(path)
            if decompressed.name != path:
                self.files[key] = decompressed.name

    def matchfile(self):
        '''Matches all file objects to a known file format'''

        for key, path in self.files.items():
            with open(path, 'rb') as fileobj:
                matcher = getmatcher(key)
                name, version, error = matcher.matchfile(fileobj)
                if error is not None:
                    self.source.helper.emitsequence(error)
                    raise AssertionError("Error with message occurred")
                else:
                    self.data['attrs']['engines'][key] = (name, version)
                    self.engines[key] = matcher[name][version]

    def checkengine(self):
        '''Checks to ensure the current profile matches the file engines'''

        name, version = self.data['attrs']['engines']['matched']
        profile = self.source.parameters.profile
        assert profile.engine == name and profile.version == version

    def ishierarchical(self):
        return self.parent().ishierarchical()

# LINKING
# -------


@logger.init('xlpy', 'DEBUG')
class IntegratedFiles(base.BaseObject):
    '''Definitions for the sum of all XL Discoverer files submitted'''

    def __init__(self):
        super(IntegratedFiles, self).__init__()

        self.offset = 0
        self.rows = []
        self.ignored = set()

        self.source = weakref.proxy(self.app.discovererthread)
        self.parsematched = matched.ProcessMatchedData()
        self.parsespectra = None
        self.setfiles()

    def __iter__(self):
        for index, row in enumerate(self.rows):
            if index not in self.ignored:
                yield row

    def __getitem__(self, index):
        return self.rows[index]

    def __len__(self):
        return len(self.rows)

    #      SETTERS

    def setfiles(self):
        '''Sets the key files and initializes the rows'''

        files = input_files.INPUT_FILES.get_table(int(self.source.quantitative))
        self.mode = files['current']
        self.files = weakref.proxy(files[self.mode])
        self._filechecker()

        self.source.rundata.mode = int(self.ishierarchical())
        for items in self.files.iterrows(use_attrs=True):
            self.newrow(items)

    #      PUBLIC

    def newrow(self, files):
        self.rows.append(FileRow(self, files))

    def ishierarchical(self):
        return self.mode == 'hierarchical'

    def delete(self, index):
        '''Calls the destructor for the objects within the row'''

        row = self.rows.pop(index)
        row.delete()

    def reindex(self):
        '''Reindexes the rows after deleting entries'''

        for index, row in enumerate(self.rows):
            if index != row.index:
                row.reindex(index)

    @logger.call('xlpy', 'debug')
    def update(self):
        for row in self.rows:
            row.update()

    @logger.call('xlpy', 'debug')
    def deleteignored(self):
        '''Deletes all ignored entries and reindexes each item'''

        for index in sorted(self.ignored, reverse=True):
            self.delete(index)
        self.ignored.clear()
        self.reindex()

        if not len(self):
            self.source.isrunning = False

    def rowcaller(self, key):
        '''Calls a given method over all rows'''

        caller = op.methodcaller(key)
        for index, row in enumerate(self.rows):
            try:
                caller(row)
            except (AssertionError, TypeError):
                yield index

    checkfile = wrappers.ignore('000')(partial(rowcaller, key='checkfile'))
    matchfile = wrappers.ignore('001')(partial(rowcaller, key='matchfile'))
    checkengine = wrappers.ignore('002')(partial(rowcaller, key='checkengine'))

    def unzipfiles(self):
        # list is required or generator never exhausted
        list(self.rowcaller('unzipfiles'))

    #      HELPERS

    def _filechecker(self, error=exception.CODES['008']):
        '''Checks to ensure all the files are of equal length'''

        length = self.files.length
        for column in self.files.values():
            if len([i for i in column if i]) != length:
                self.source.error.emit(error, Exception)
                self.source.isrunning = False
                return
