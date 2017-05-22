'''
    Resources/binary
    ________________

    File headers for recognizing and processing binary data.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from namedlist import namedlist

import tables as tb

__all__ = [
    'BINARY_FILES',
]

# ENUMS
# -----

COMPRESSION = tb.Enum([
    'zip',
    'tar',
    'gzip',
    'bzip2'
])


# OBJECTS
# -------


BinaryFile = namedlist("BinaryFile", [
    'format',
    'header',
    ('extension', None),
    ('compression', None),
])


# DATA
# ----


BINARY_FILES = {
    'bz2': BinaryFile('bzip2',
        header=b"\x42\x5a\x68",
        extension=['.bz2'],
        compression=COMPRESSION['bzip2']),
    'gz': BinaryFile('gzip',
        header=b"\x1f\x8b\x08",
        extension=['.gz'],
        compression=COMPRESSION['gzip']),
    'HDF5': BinaryFile('HDF5',
        header=b'\x89HDF\r\n',
        extension=['.h5', '.hdf5']),
    'RAW': BinaryFile('RAW',
        header=b'\x01\xa1F\x00i\x00n\x00n\x00i\x00g\x00a\x00n',
        extension=['.raw']),
    'SQLite3': BinaryFile('SQLite3',
        header=b'SQLite format 3\x00',
        extension=['.db', '.sqlite']),
}
