'''
    Objects/Documents/Transitions/Cache/document
    ____________________________________________

    HDF5 data cache for the transitions document store.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import os
import shutil
import six

import tables as tb

from xldlib.objects import pytables
from xldlib.resources import paths
from xldlib.utils import decorators, logger
from xldlib.utils.io_ import high_level

# load objects/functions
from .file import TransitionsFileCache
from .save import IO_ROWS

# DOCUMENT
# --------


@logger.init('document', 'DEBUG')
class TransitionsDocumentCache(pytables.Root):
    '''Definitions for the spectral store from a transitions document'''

    # PATH SUFFIX
    # -----------
    _child = TransitionsFileCache
    suffix = 'c'

    # READ/WRITE
    # ----------
    iorows = IO_ROWS

    def __init__(self):
        super(TransitionsDocumentCache, self).__init__()

    #     MAGIC

    def __iter__(self):
        '''Iterate over all the children in the group'''

        keys = sorted(self.root._v_groups, key=int)
        for key in keys:
            yield self[key]

    def __len__(self):
        return len(self.root._v_groups)

    def __getitem__(self, item):
        '''Returns the item from the key or slice object'''

        if isinstance(item, slice):
            items = range(*item.indices(len(self)))
            return [self._child(self, i) for i in items]
        else:
            return self._child(self, item)

    if six.PY2:
        # slice operations are depricated in Py3.x
        def __getslice__(self, start, stop):
            return self.__getitem__(slice(start, stop))

    #     PUBLIC

    @decorators.overloaded
    def new(self, path=paths.FILES['transition']):
        '''Defines a blank HDF5 data cache'''

        self._new(path + self.suffix)
        self.root = self.file.root

    def open(self, path, mode='a'):
        '''Opens a pre-existing file object'''

        self._open(path + self.suffix, mode=mode)
        self.root = self.file.root

    def close(self):
        '''Closes an open file object'''

        path = self.path
        self._close()
        self.root = None

        self.cleanup(path)

    def save(self, path, indexes):
        '''Reset the path and dump both files to a shared location'''

        if path + self.suffix != self.path:
            self.saveas(path, indexes)
            self.close()

            self.open(path)
        else:
            self.flush()

    def saveas(self, path, indexes):
        '''Copies the current file to a new location'''

        if indexes is None or indexes == range(len(self)):
            self.shutilsave(path)
        else:
            self.tbsave(path, indexes)

    def shutilsave(self, path):
        '''File system copy of the full file -- much faster'''

        self.flush()
        shutil.copy2(self.path, path + self.suffix)

    def tbsave(self, path, indexes):
        '''Uses the HDF5 copy mode to copy nodes to a new file'''

        newfile = tb.File(path + self.suffix, mode='w')
        for index in indexes:
            row = self[index]
            row.copy(newparent=newfile.root,
                newname=str(index),
                recursive=True)

        newfile.close()

    def addrow(self, row):
        return self._child(self, row)

    #    REMOVAL

    def delete_file(self, row, reindex=True):
        '''Deletes the given file and reindexes the child groups'''

        self[str(row)].remove(recursive=True)

        if reindex:
            self.reindex()

    def reindex(self):
        '''Reindexes the child groups to have sequential primary keys'''

        for index, row in enumerate(self):
            if str(index) != row.group._v_name:
                row.rename(newname=str(index))

    #     HELPERS

    def cleanup(self, path):
        '''Cleans up the file object on close if in the TMP_DIR'''

        if path is not None and os.path.dirname(path) == high_level.TMP_DIR:
            high_level.remove_file(path)
