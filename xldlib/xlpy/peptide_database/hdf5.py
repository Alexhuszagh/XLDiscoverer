'''
    XlPy/Peptide_Database/hdf5
    __________________________

    Utilities for linearizing and writing to HDF5.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from models import params


class HDF5Utils(object):
    '''Provides utilities to simplify converting to HDF5 structures'''

    # ------------------
    #       PUBLIC
    # ------------------

    def linearize(self):
        '''
        Converts the namedtuples to arrays for fast searching, as well
        as compacts the overall data size to reduce the total virtual
        memory usage (standard, decoy is variable but ~2x).
        :
            Format: bytes (numpy), missing ~280 for Pyobjects, [] elements

            1 mod (M), 178 aa -> 12528 bytes [197]
            2 mods (Q, N, M), 178 aa -> 20292 bytes [385]
            3 mods (Q, N, M, C), 178 aa -> 24018 bytes [454]

            1 mod (M), 511 aa -> 33186 bytes [534]
            2 mods (Q, N, M), 511 aa -> 61085 bytes [1051]
            3 mods (Q, N, M, C), 511 aa -> 69026 bytes [1186]

            1 mod (M), 742 aa -> 34059 bytes [549]
            2 mods (Q, N, M), 742 aa -> 63527 bytes [1093]
            3 mods (Q, N, M, C), 742 aa -> 73391 (np) bytes [1261]

            1 mod (M), 1650 aa -> 78732 bytes [1338]
            2 mods (Q, N, M), 1650 aa -> 163956 bytes [2784]
            3 mods (Q, N, M, C), 1650 aa -> 182059 (np) bytes [3091]

        Can do ~6000x the 3 mods case for 1gb of virt mem, or ~ 9e6 aas
        with 3 mods or ~2.1e7 aas with 1 mod
        '''

        # mode -> {'standard', 'decoy'}
        for mode, searchables in self.searchables.items():
            keys = list(searchables.keys())
            for key in keys:
                dset_key = '{}/{}'.format(mode, key)
                self.linearize_key(dset_key, searchables[key])

    def linearize_key(self, key, items):
        '''
        Linearizes a given key to a numpy array
        :
            key -> 'standard/(85.9826354,)'
        '''

        if key not in self.grp:
            grp = self._new_keys(key)
        else:
            grp = self.grp[key]
        values = zip(*items)
        for index, value in enumerate(values):
            field = self.search_fields[index]
            self._write_fields(grp, field, value)

        # clear the list (assume Py2.7, so no list.clear())
        del items[:]

    # ------------------
    #   PRIVATE -- HDF5
    # ------------------

    def _new_keys(self, key):
        '''Adds new keys with compression filters for pep search databases'''

        grp = self.grp.create_group(key)
        kwds = params.FINGERPRINT_HDF5
        # max length of an ID mnemonic is 11
        grp.create_dataset('id', dtype='S11', **kwds)
        for key in {'peptide', 'formula', 'modifications'}:
            dtype = getattr(self, "{}_dtype".format(key))
            grp.create_dataset(key, dtype=dtype, **kwds)

        grp.create_dataset('start', dtype=int, **kwds)
        grp.create_dataset('mass', dtype=float, **kwds)

        return grp

    def _write_fields(self, grp, field, value):
        '''Writes values to an HDF5 dataset'''

        entry = grp[field]
        (rows, length) = entry.shape
        entry.resize((rows + 1, length))

        val_length = len(value)
        grp[field][0, : val_length] = value
