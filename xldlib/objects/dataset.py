'''
    Objects/dataset
    _______________

    Base dataset object designed for inheritance.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.

    >>> ds = Dataset()
    >>> ds._new('a.h5')
    >>> ds.file
    File(filename=a.h5, title='', mode='w', root_uep='/', filters=Filters(complevel=0, shuffle=False, fletcher32=False, least_significant_digit=None))
    / (RootGroup) ''

    >>> len(ds)
    0

    >>> ds._close()
    >>> ds._close()
    >>> ds.file
'''

# load modules
import tables as tb

from xldlib.qt.objects import base
from xldlib.utils.io_ import high_level

# CONSTANTS
# ---------

VLATOMS = (
    tb.VLUnicodeAtom,
    tb.ObjectAtom,
    tb.VLStringAtom
)


# OBJECTS
# -------


class Dataset(base.BaseObject):
    '''Base dataset with bindings for data attributes'''

    # COMPRESSION
    # -----------
    _filter = {
        'complevel': 5,
        'complib': 'blosc'
    }

    def __init__(self):
        super(Dataset, self).__init__()

        self.file = None
        self.root = None
        self.path = None
        self.filter = tb.Filters(**self._filter)

    def __len__(self):
        if self.file is None:
            return 0
        else:
            return self.file.root._v_attrs.length

    #       I/O

    def _new(self, path):
        '''Initiates a new PyTables file'''

        self._close()

        self.path = path
        high_level.remove_file(self.path)
        self.file = tb.File(self.path, mode='w')
        self.root = self.file.root

        self._set_len(0)

    def _open(self, path, mode='a'):
        '''Opens an existing PyTables file'''

        self._close()

        self.file = tb.File(path, mode=mode)
        self.root = self.file.root
        self.path = path

    def _close(self):
        '''Closes an open PyTables file'''

        if self.file is not None:
            self.file.close()
            self.file = None
            self.root = None
            self.path = None

    def save(self, path):
        '''Save the current object to buffer'''

        self.file.flush()
        if os.path.realpath(path) != os.path.realpath(self.path):
            self.file.copy_file(path, overwrite=True)

    def remove(self):
        '''Closes and removes the currently opened file'''

        path = self.path
        if path is not None:
            # trust the inherited class to have a "close" method
            getattr(self, "close", self._close)()
            high_level.remove_file(path)

    #      SETTERS

    def _set_len(self, length):
        '''Sets the current length for the object'''

        self.file.root._v_attrs.length = length

    #      CREATORS

    def _create_array(self, where, name, atom, title):
        '''Creates either an extendable or variable-length array'''

        if isinstance(atom, VLATOMS):
            return self.file.create_vlarray(where, name, atom, title,
                filters=self.filter)

        else:
            return self.file.create_earray(where, name, atom,
                shape=(0,),
                title=title,
                filters=self.filter)

    def _append(self, array, value):
        '''Helper for VLArrays and EArray appending (which differs)'''

        if isinstance(array, tb.VLArray):
            array.append(value)

        elif isinstance(array, tb.EArray):
            array.append([value])
