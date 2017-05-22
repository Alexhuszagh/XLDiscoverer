'''
    XlPy/Link_Finder/Search/base
    ____________________________

    Base classes with bound attributes for the lin and
    PMF searchers

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from __future__ import division

import itertools

from models import params, scans

# load objects/functions
from .pmf import PMFChecker


class PMFSettings(object):
    '''Binds settings for link searching to the class for inheritance'''

    def __init__(self):
        super(PMFSettings, self).__init__()

        self._decoy = params.MASS_FINGERPRINT['search_decoys']
        self.dbs = ['standard', 'decoy'] if self._decoy else ['standard']
        self.unique = {i.decode('utf-8') for i in self.data.unique_ids}

        if self.source.find_unmatched:
            # TODO: no searchables so need to update queries
            import pdb, sys; pdb.Pdb(stdout=sys.__stdout__).set_trace()

            self.modifications = self.unpack_modifications()
            self.mods_length = (max(self.modifications) // 10) + 1
            self.protein_names = self.unpack_proteinnames()

    def unpack_modifications(self):
        '''Unpacks the modification data into a dictionary for quick lookups'''

        mods = {}
        modifications = self.searchables.attrs['modification'].astype(str)
        ids = self.searchables.attrs['modification_ids']
        for id_, modification in zip(ids, modifications):
            mods[id_] = modification

        return mods

    def unpack_proteinnames(self):
        '''Unpacks the modification data into a dictionary for quick lookups'''

        names = {}
        protein_names = self.searchables.attrs['protein_names'].astype(str)
        ids = self.searchables.attrs['protein_ids'].astype(str)
        for id_, name in zip(ids, protein_names):
            names[id_] = name

        return names


class PMFBase(PMFSettings):
    '''
    Provides a convenient parent class for link searching and
    making algorithms.
    '''

    _single = 1

    def __init__(self, file_key, xlkey, parent):
        self.source = parent.source
        self.file = file_key
        self.xler = parent.xler
        self.data = parent.data
        self.engine = parent.engine

        self._ppm_thresh = params.MASS_ERRORS['thresholds']['ppm'] * 1e-6

        if self.source.find_unmatched:
            self.precursor_scans = self.get_precursors()
            search_key = 'searchables/{}'.format(xlkey)
            self.searchables = self.source.rundata[search_key]

        super(PMFBase, self).__init__()

    def get_precursors(self):
        '''Finds the precursor scan HDF5 group'''

        prec_key = sorted(scans.SCANS["raw_types"][self.source.input_type])[0]
        key = '/raw/{0}/{1}'.format(prec_key, self.file)
        return self.source.rundata[key]

    def search_singles(self, links, scan, index):
        '''
        Searches for single links upon the exhaustion of the double
        combinations, using all theoretical permutations of singles
        from a limited db and compares it to the raw precursor scan data.
        '''

        index_range = list(range(len(scan.start)))
        combinations = itertools.combinations(index_range, self._single)
        for indexes in combinations:
            scan_tmp = scan._repack(indexes)
            cls = PMFChecker(scan_tmp, index, indexes[0], self)
            cls.check_single()
            links += cls.matched
