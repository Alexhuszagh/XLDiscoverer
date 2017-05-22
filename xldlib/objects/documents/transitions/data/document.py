'''
    Objects/Documents/Transitions/Data/document
    ___________________________________________

    Memory-mapped data for the transitions document hierarchy and
    structure.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import contextlib
import copy
import six

from collections import defaultdict

from xldlib import chemical
from xldlib.definitions import partial
from xldlib.objects import mappedfile
from xldlib.onstart.main import APP
from xldlib.resources import paths
from xldlib.resources.parameters import defaults
from xldlib.resources import version
from xldlib.utils import logger, serialization

from .file import TransitionsFileData
from .. import cache, tools

# CONSTANTS
# ---------

DEFAULT_KEYS = (
    'include_mixed_populations',
)

DOCUMENT_ATTRS = (
    'fragments',
    'isobaric',
    'crosslinkers',
    'include_mixed_populations',
    'profile',
    'profiles',
    'retentiontime_lock'
)


# TEMPLATES
# ---------


NEWFILE = {
    'files': [],
    'attrs': {}
}


# WITH STATEMENTS
# ---------------


@contextlib.contextmanager
def togglememory(document, state=None):
    '''Toggles the memory attribute of the document for the context block'''

    # invert the document state and store the old state
    oldstate = document.memory
    if state is None:
        state = not oldstate
    document.memory = state

    try:
        yield document
    finally:
        document.memory = oldstate


# DOCUMENT
# --------


@serialization.register('TransitionsDocument')
@logger.init('document', 'DEBUG')
class TransitionsDocument(mappedfile.File):
    '''Definitions for the mapping data stores in the document'''

    # CHILD
    # -----
    _child = TransitionsFileData

    # ATEXIT
    # ------
    _forcesave = False

    # READ/WRITE
    # ----------
    iorows = cache.TransitionsDocumentCache.iorows

    def __init__(self, path=None, data=None, registered=False):
        super(TransitionsDocument, self).__init__(path, data, registered)

        self.memory = False
        self.cache = None
        self.togglememory = partial(togglememory, self)

    #     MAGIC

    def __len__(self):
        '''Number of files within the document'''

        return len(self.data['files'])

    def __iter__(self):
        '''Iterate over all child nodes in the document'''

        for index in range(len(self)):
            yield self[index]

    def __getitem__(self, item):
        '''Returns a specific object or from a slice'''

        files = self.data['files']
        if isinstance(item, slice):
            items = range(*item.indices(len(self)))
            return [self._child(self, str(i), files[i]) for i in items]
        else:
            transitionfile = files[int(item)]
            return self._child(self, str(item), transitionfile)

    def __delitem__(self, item):
        raise NotImplementedError

    def __setitem__(self, item):
        raise NotImplementedError

    if six.PY2:
        # slice operations are depricated in Py3.x
        def __getslice__(self, start, stop):
            return self.__getitem__(slice(start, stop))

        def __delslice__(self, start, stop):
            return self.__delitem__(slice(start, stop))

        def __setslice__(self, start, stop, value):
            return self.__setitem__(slice(start, stop), value)

    @serialization.tojson
    def __json__(self, indexes=None):
        '''Implementation to dump an object as a msgpack'''

        data = self.data
        if indexes is not None:
            data = data.copy()
            data['files'] = [data['files'][i] for i in indexes]

        return {
            'path': self.path,
            'data': data
        }

    #     PUBLIC

    #       I/O

    @classmethod
    def new(cls, path=None, blank=False):
        '''Defines the data cache and the metadata'''

        inst = super(TransitionsDocument, cls).new(path, blank)
        inst.cache = cache.TransitionsDocumentCache()
        inst.cache.new(inst.path)

        inst.setattr('type', 'document')
        inst.setattr('file_type', 'transition')
        inst.setattr('software_version', version.BUILD)

        if not blank:
            inst.setparameters()

        return inst

    @classmethod
    def open(cls, path, mode='a'):
        '''Opens a pre-existing file object'''

        inst = super(TransitionsDocument, cls).open(path)
        inst.cache = cache.TransitionsDocumentCache()
        inst.cache.open(inst.path, mode)

        assert inst.file_type == 'transition'
        return inst

    def close(self, save=False):
        '''Closes the database to avoid pickling writes to file'''

        if save:
            self.save()

        self.cache.close()
        super(TransitionsDocument, self).close()

    def save(self, path=None, indexes=None, pickling=None):
        '''Reset the path and dump both files to a shared location'''

        if path is None:
            path = self.path
        if pickling is None:
            pickling = defaults.DEFAULTS['enable_pickle']

        self.path = path
        if self.registered:
            serialized = self.__json__(indexes)
            serialization.serialize(serialized, path, pickling)
            self.cache.save(path, indexes)

    #    EXTEND

    def addrow(self):
        '''Appends a row to the filelist'''

        index = len(self.data['files'])
        self.cache.addrow(index)

        row = self._child.new(self, str(index))
        self.append(row)

        return row

    def append(self, row):
        self.data['files'].append(row.data)

    #    HIERARCHY

    def getfromlevels(self, levels, memory=None):
        '''Returns the HDF5-wrapped group from the levels'''

        if memory is None:
            memory = self.memory

        with self.togglememory(memory):
            levels = [i for i in levels if i is not None]
            if len(levels) == 0:
                return self
            elif len(levels) == 1:
                return self.get_file(*levels)
            elif len(levels) == 2:
                return self.get_labels(*levels)
            elif len(levels) == 3:
                return self.get_crosslink(*levels)
            elif len(levels) == 4:
                return self.get_charge(*levels)
            elif len(levels) == 5:
                return self.get_isotope(*levels)

    def get_file(self, row):
        return self[row]

    def get_labels(self, row, labels):
        return self[row][labels]

    def get_crosslink(self, row, labels, crosslink):
        return self[row][labels][crosslink]

    def get_charge(self, row, labels, crosslink, charge):
        return self[row][labels][crosslink][charge]

    def get_isotope(self, row, labels, crosslink, charge, isotope):
        return self[row][labels][crosslink][charge][isotope]

    #    REMOVAL

    def delete_file(self, row, reindex=True):
        '''Deletes the given file and reindexes the child groups'''

        self.cache.delete_file(row, reindex)
        del self.data['files'][int(row)]

    def reindex(self):
        self.cache.reindex()

    #    SETTERS

    def setparameters(self):
        '''Sets the transition document parameters prior to searching'''

        self.__setsource()
        self.__setdefaults()
        locked = self.profile.islocked(chemical.Molecule)
        self.setattr('retentiontime_lock', locked)

    def setglobal(self):
        self.setattr('global', tools.getglobal(self))

    def __setsource(self):
        '''Sets the runtime parameters from the source file'''

        source = APP.discovererthread
        for key, value in source.parameters.items():
            if key not in {'search', 'spectra'}:
                self.setattr(key, value)

    def __setdefaults(self):
        '''Sets the configuration defaults'''

        for key in DEFAULT_KEYS:
            self.setattr(key, defaults.DEFAULTS[key])

    #    HELPERS

    @staticmethod
    def _new(blank):
        return copy.deepcopy(NEWFILE)

    @staticmethod
    def _newpath():
        return paths.FILES['transition']

    def flush(self):
        self.cache.flush()

    def setupmemo(self):
        self.memo = defaultdict(dict)

    def cleanupmemo(self):
        del self.memo

    def init_cache(self):
        '''Initializes the transitions cache for each file'''

        for transitionfile in self:
            transitionfile.init_cache()
