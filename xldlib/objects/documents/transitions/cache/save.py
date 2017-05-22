'''
    Objects/Documents/Transitions/Cache/save
    ________________________________________

    Optimized settings for creating new files from a given spectral item.

    Some code in here is modified from the PyTables framework, specifically
    tables.node, which was written by:
        Author: Ivan Vilata i Balaguer - ivan@selidor.net
        Created: 2005-02-11
        License: BSD

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import math
import six

import numpy as np
import tables as tb

from xldlib.objects import pytables


# CONSTANTS
# ---------
# Number of rows before flushing/loading PyTables to disk
# during read/write operations
# ~86 kb/item/5000 scans based on float64s

IO_ROWS = 5000


# HIERARCHY
# ---------


def get_parent(src, newparent):
    '''Returns the destination file and path'''

    if hasattr(newparent, '_v_file'):
        # from node
        return newparent._v_file, newparent._v_pathname

    elif isinstance(newparent, six.string_types):
        # from path
        return src.v_file, newparent

    else:
        msg = "newparent is not a node or a path {}".format(newparent)
        raise TypeError(msg)


def is_same_node(src, newfile, newpath, newname):
    '''
    Checks whether the new item would overwrite itself, that is,
    the source node and end node would be the same
    '''

    return all((
        src._v_file is newfile,
        newpath == src._v_parent._v_pathname,
        newname == src._v_name
    ))


# COPIERS
# -------


@pytables.silence_naturalname
def copy_group(src, newparent=None, newname=None, **kwds):
    '''
    Copies an item from the src group to the dst holder, using PyTables
    built-in copy for the single group but with manual control of
    sub-structures.
    '''

    recursive = kwds.pop('recursive', False)
    child = src._f_copy(newparent=newparent, newname=newname, **kwds)

    if recursive:
        for group in src._v_groups.values():
            copy_group(group, newparent=child, **kwds)

        for leaf in src._v_leaves.values():
            copy_leaf(leaf, child, **kwds)

    return child


@pytables.silence_naturalname
def copy_leaf(src, newparent=None, newname=None, **kwds):
    '''Copies a PyTables leaf node, with targeted copiers.'''

    # Set default arguments.
    if newparent is None and newname is None:
        raise tb.NodeError("Please specify either a newparent or newnode")

    if newparent is None:
        newparent = src._v_parent
    if newname is None:
        newname = src._v_name

    newfile, newpath = get_parent(src, newparent)
    if is_same_node(src, newfile, newpath, newname):
        raise tb.NodeError("Cannot copy over itself")

    if isinstance(src, tb.Array):
        _copy_array(src, newparent, newname, **kwds)


# PRIVATE COPIERS
# ---------------


def _copy_array(src, newparent, newname, **kwds):
    '''
    Copies a single array, but skips the default copying shape to define
    its own read-write using custom blockshapes.
    '''

    if isinstance(src, tb.EArray):
        return _copy_earray(src, newparent, newname, **kwds)

    elif isinstance(src, tb.CArray):
        # earray inherits carray, so comes second
        return _copy_carray(src, newparent, newname, **kwds)

    elif isinstance(src, tb.VLArray):
        return _copy_vlarray(src, newparent, newname, **kwds)

    else:
        # remaining, straight array
        return newparent._v_file.create_array(where=newparent,
            name=newname,
            obj=np.array(src))


# CARRAY
# ------


def _copy_carray(src, newparent, newname, **kwds):
    '''Chunked array copy machinery'''

    newarray = newparent._v_file.create_carray(where=newparent,
        name=newname,
        atom=src.atom,
        shape=src.shape,
        title=src.title,
        filters=src.filters,
        chunkshape=src.chunkshape,
        byteorder=src.byteorder)

    for index in range(0, int(math.ceil(src.nrows / IO_ROWS) + 1)):
        start = index * IO_ROWS
        end = start + IO_ROWS
        newarray[start:end, ] = src[start:end, ]

    return newarray


# EARRAY
# ------


def _new_earray(src, newparent, newname, **kwds):
    '''Creates an empty copy of the initial array to be filled later'''

    # set the extendable dimension
    shape = list(src.shape)
    shape[src.extdim] = 0

    return newparent._v_file.create_earray(where=newparent,
        name=newname,
        atom=src.atom,
        shape=tuple(shape),
        title=src.title,
        filters=src.filters,
        expectedrows=src._v_expectedrows,
        chunkshape=src.chunkshape,
        byteorder=src.byteorder)


def _copy_earray(src, newparent, newname, **kwds):
    '''Creates and copies data into a new extendable array'''

    newarray = _new_earray(src, newparent, newname, **kwds)

    # copy over the data
    for index in range(0, int(math.ceil(src.shape[src.extdim] / IO_ROWS) + 1)):
        slices = [slice(None)] * len(src.shape)
        slices[src.extdim] = slice(index * IO_ROWS, (index + 1) * IO_ROWS)
        read = src[tuple(slices)]

        newarray.append(read)
        # explicitly call cleanup to avoid gc collect issues
        del read

    return newarray


# VLARRAY
# -------


def _copy_vlarray(src, newparent, newname, **kwds):
    '''Variable length array copy machinery'''

    newarray = newparent._v_file.create_vlarray(where=newparent,
        name=newname,
        atom=src.atom,
        title=src.title,
        filters=src.filters,
        expectedrows=src._v_expectedrows,
        chunkshape=src.chunkshape,
        byteorder=src.byteorder)

    for row in src.iterrows():
        newarray.append(row)

    return newarray
