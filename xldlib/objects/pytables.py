'''
    Objects/pytables
    ________________

    Group and root wrappers for PyTables objects.
'''

# load modules
import tables as tb

from xldlib import exception
from xldlib.qt.objects import base

from . import dataset

# DECORATORS
# ----------

silence_naturalname = exception.silence_warning(tb.NaturalNameWarning)
silence_tbperformance = exception.silence_warning(tb.PerformanceWarning)


# DATA
# ----


class Root(dataset.Dataset):
    '''Definitions for PyTables root attributes'''

    #     MAGIC

    def __len__(self):
        return len(self.root._v_groups)

    def __eq__(self, other):
        return self.root == other.root

    def __ne__(self, other):
        return not self == other

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        return isinstance(exc_val, (OSError,))

    #  PUBLIC FUNCTIONS

    def flush(self):
        self.file.flush()

    @silence_naturalname
    def create_group(self, *args, **kwds):
        return self.file.create_group(self.root, *args, **kwds)

    #    CHECKERS

    def hasattr(self, key):
        '''Return if the HDF5 attributes contains the key'''

        # attributes are much faster using the attribute interface
        return hasattr(self.root._v_attrs, key)

    def hasgroup(self, key):
        '''Returns if the HDF5 groups contains the key'''

        # groups are much faster using the mapping interface
        return key in self.root._v_groups

    #    SETTERS

    def setattr(self, key, value, recurse=False):
        '''Sets the HDF5 attributes for the filegroup'''

        setattr(self.root._v_attrs, key, value)
        if recurse:
            for item in self:
                item.setattr(key, value, recurse=True)

    #    GETTERS

    def getattr(self, key, default=None):
        '''Returns an HDF5 attribute from the root'''

        # attribute reading much faster using attribute interface
        return getattr(self.root._v_attrs, key, default)

    def getattrs(self, attrs):
        return map(self.getattr, attrs)

    def getgroup(self, row):
        '''Returns an HDF5 attribute from the root'''

        # group reading faster using mapping interface
        return self.root._v_groups[str(row)]


class Group(base.BaseObject):
    '''Definitions for PyTables group attributes'''

    #     MAGIC

    def __iter__(self):
        return iter(self.group._v_groups)

    def __getitem__(self, key):
        return self.group._v_groups[key]

    def __len__(self):
        return len(self.group._v_groups)

    def __eq__(self, other):
        return self.group == other.group

    def __ne__(self, other):
        return not self == other

    # PUBLIC FUNCTIONS

    @silence_naturalname
    def copy(self, **kwds):
        '''Unoptimized implementation from PyTables for average use'''

        self.group._f_copy(**kwds)

    @silence_naturalname
    def move(self, *args, **kwds):
        try:
            self.group._f_move(*args, **kwds)
        except RuntimeError:
            # internal PyTables error, item is already moved
            pass

    @silence_naturalname
    def rename(self, newname, overwrite=False):
        try:
            self.group._f_rename(newname, overwrite)
        except RuntimeError:
            # internal PyTables error, item is already moved
            pass

    def remove(self, **kwds):
        self.group._f_remove(**kwds)

    @silence_naturalname
    def create_array(self, *args, **kwds):
        return self.group._v_file.create_array(self.group, *args, **kwds)

    @silence_naturalname
    def create_earray(self, *args, **kwds):
        return self.group._v_file.create_earray(self.group, *args, **kwds)

    @silence_naturalname
    def create_vlarray(self, *args, **kwds):
        return self.group._v_file.create_vlarray(self.group, *args, **kwds)

    @silence_naturalname
    def create_group(self, *args, **kwds):
        return self.group._v_file.create_group(self.group, *args, **kwds)

    @silence_naturalname
    def create_hard_link(self, *args, **kwds):
        return self.group._v_file.create_hard_link(self.group, *args, **kwds)

    #    CHECKERS

    def hasattr(self, key):
        '''Returns if the HDF5 attributes contains the key'''

        # attributes are much faster using the attribute interface
        return hasattr(self.group._v_attrs, key)

    def hasgroup(self, key):
        '''Returns if the HDF5 groups contains the key'''

        # groups are much faster using the mapping interface
        return key in self.group._v_groups

    #    GETTERS

    def getattr(self, key):
        '''Sets the HDF5 attributes for the filegroup'''

        # attribute reading much faster using attribute interface
        return getattr(self.group._v_attrs, key)

    def getattrs(self, attrs):
        return map(self.getattr, attrs)

    def getgroup(self, key):
        '''Returns if the HDF5 groups contains the key'''

        # group reading faster using mapping interface
        return self.group._v_groups[key]

    #    SETTERS

    def setattr(self, key, value, recurse=False):
        '''Sets the HDF5 attributes for the filegroup'''

        setattr(self.group._v_attrs, key, value)
        if recurse:
            for item in self:
                item.setattr(key, value, recurse=True)

    def setattrs(self, **kwds):
        for key, value in kwds.items():
            self.setattr(key, value)

    #    DELETERS

    def delattr(self, key):
        '''Deletes the HDF5 attributes for the filegroup'''

        self.group._f_delattr(key)
