'''
    XlPy/Link_Finder/maker/pmf
    __________________________

    Tools to compile the XL-MS information into a namedtuple
    to simplify data export.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from __future__ import division

import itertools
import numpy as np

from models import params, scans
from xldlib import chemical
from xldlib.definitions import re
from xldlib.utils import iterables, masstools

# load objects/functions
from collections import defaultdict

from models.data import unpack_data
from models.params.residues import RESIDUE_TYPES
from ..objects import Mass, PMFTuple
from xlpy.matched.core import get_engine
from xlpy.matched.names import add_name
from xlpy.tools.mass import PrecursorMass


class PMFMaker(object):
    '''
    Object which adds the single data into the matched scans and then
    creates a special.
    '''

    add_name_ = add_name
    _parent_attrs = {'matched', '_ppm_thresh', 'data', 'xler', 'scan_data'}
    _base_attrs = {'modifications', 'protein_names',
                   'unique', 'source', 'mods_length'}

    def __init__(self, query, search, index, parent, base):
        '''
        Calls the constructor class and binds instance attributes,
        including the namedtuple query, the search database to find
        potential matches, and the index in the query to do the search.
        '''
        super(PMFMaker, self).__init__()

        self.query = query
        self.search = search
        self.index = index
        self.data_index = parent.index
        for key in self._parent_attrs:
            setattr(self, key, getattr(parent, key))
        for key in self._base_attrs:
            setattr(self, key, getattr(base, key))
        self.engine = get_engine(self.data)

        self.unpack_data = unpack_data.__get__(self)

        indexes = self.get_indexes()
        self.ambiguous = len(indexes) == 1
        self.process_data(indexes)

    def get_indexes(self):
        '''Extract the match indexes for the given scans'''

        mass = masstools.mz(self.search['mass'], self.query.z, 0)
        exper = self.query.exper[self.index]
        indexes, = np.where(abs(exper - mass) / mass <= self._ppm_thresh)

        return indexes

    def process_data(self, indexes):
        '''
        Adds to the parent data and creates a link object with simple indexes
        For the data attributes, need to modify the following keys (list
        elements):
            {'id', 'mods', 'score', 'ev', 'fraction', 'precursor_num',
             'start'}
        '''

        for match_idx in indexes:
            index = len(self.data['id'])
            self.add_data(match_idx)
            self.make_link(index)

    # ------------------
    #     DATA UTILS
    # ------------------

    def add_data(self, match_idx):
        '''
        Adds a row to the data entries with data from the matched pair,
        the precursor scan, and previous matched data to add the matched
        single into the standard workflow.
        '''

        self._add_crosslink_types()
        self._add_nans()
        self._add_query_data()
        self._add_search_data(match_idx)
        self._add_ids()
        self._add_mods(match_idx)

    def _add_crosslink_types(self):
        '''
        Adds data typical for crosslink types and therefore should be
        the same for both peptides in the link.
        '''

        idx = self.data_index[0]
        for key in list(scans.SCANS['crosslink_types']) + ['fraction']:
            self.data[key].append(self.data[key][idx])

    def _add_nans(self):
        '''Adds null values specific to sequenced ions'''

        for key in ['score', 'ev', 'num', 'rank']:
            self.data[key].append(np.nan)

    def _add_query_data(self):
        '''Adds data specific to the query, such as mass'''

        self.data['m/z'].append(self.query.exper[self.index])
        self.data['z'].append(self.query.z)
        self.data['ppm'].append(self.query.ppm[self.index] * 1e6)

    def _add_search_data(self, match_idx):
        '''
        Adds data specific to the matched peptide, such as sequence,
        peptide start and uniprot ID
        '''

        id_ = self.search['id'][match_idx].decode('utf-8')
        self.data['id'].append(id_)

        self.data['name'].append(self.protein_names.get(id_, 'decoy'))

        peptide = self.search['peptide'][match_idx].decode('utf-8')
        self.data['peptide'].append(peptide)

        self.data['start'].append(self.search['start'][match_idx])

        formula = self.search['formula'][match_idx].decode('utf-8')
        self.data['formula'].append(chemical.Molecule(formula))

    def _add_ids(self):
        '''Adds ID-dependent data to the spreadsheet'''

        id_ = self.data['id'][-1]
        self.add_name_(id_)
        if id_ not in self.unique:
            self.data['unique_ids'].append(id_)
            self.unique.add(id_)

    def _add_mods(self, match_idx):
        '''
        Adds mods by calculating all permutations of positions and then
        adding the dataset to self.data
        '''

        res_mods = self.group_mods_by_res(match_idx)
        permutations = self.get_mod_permutations(res_mods)
        mods = self.make_mods(permutations)
        mods = self.flatten_mods(mods)
        self.data['mods'].append(mods)

    def group_mods_by_res(self, match_idx):
        '''Groups the residue lists by modifications'''

        mods = self.convert_mods(match_idx)
        res_mods = defaultdict(list)
        for mod in mods:
            if mod in self.source.fragments:
                res = self.source.fragments[mod][1]
            else:
                res = self.engine['mods'][mod][1]
            res_mods[res].append(mod)

        return res_mods

    def convert_mods(self, match_idx):
        '''Converts abck the modifications from the HDF5 format'''

        modifications = self.search['modifications'][match_idx]
        mods = []
        for index in range(0, len(modifications), self.mods_length):
            mod = int(modifications[index: index+self.mods_length])
            mods.append(mod)

        return [self.modifications[i] for i in mods]

    def get_mod_permutations(self, res_mods):
        '''
        Calculates all possible permutations of the modifications with
        some redundancy given the residue specificity for each mod.
        '''

        mod_permutations = defaultdict(list)
        peptide = self.data['peptide'][-1]
        for res, mod_list in res_mods.items():
            pattern = res.replace(',', '|')
            # protein prospector 1 indexes their mods
            indexes = (i.start() + 1 for i in re.finditer(pattern, peptide))
            # consider N-term/c-term mods
            for key in RESIDUE_TYPES.terms:
                if any(i in res for i in RESIDUE_TYPES[key]):
                    indexes = itertools.chain(indexes, [self.engine[key]])

            # sample all permutations
            count = len(mod_list)
            perms = itertools.permutations(indexes, count)
            # perms should be [[comb], [comb]]
            mod_permutations[tuple(mod_list)] = tuple(perms)
        return mod_permutations

    @staticmethod
    def make_mods(mod_permutations):
        '''Returns a list of all possible mod combinations'''

        order = sorted(mod_permutations.keys())
        generator = (mod_permutations[k] for k in order)
        perms = tuple(iterables.mod_product(*generator))

        mods = []
        for mod_perm in perms:
            mod = defaultdict(list)
            for idx, pos_list in enumerate(mod_perm):
                for pos_index, pos in enumerate(pos_list):
                    mod[order[idx][pos_index]].append(pos)
            mods.append(mod)
        return mods

    @staticmethod
    def flatten_mods(mods):
        '''Flattens the mods to remove redundant uncertain reporting'''

        flattened = {'certain': {}, 'neutralloss': [0.]}
        keys = list(mods[0].keys())
        for key in keys:
            value = mods[0][key]
            if all(mod[key] == value for mod in mods):
                flattened['certain'][key] = value
                for mod in mods:
                    del mod[key]

        # need to remove empty lists to prevent trailing ';'
        if any(mod for mod in mods):
            flattened['uncertain'] = mods
        else:
            flattened['uncertain'] = []

        return flattened

    # ------------------
    #     LINK UTILS
    # ------------------

    def make_link(self, idx):
        '''Creates the link object for the single type'''

        total = self.data_index[:]
        total.append(idx)

        ppm = self.query.ppm[self.index] * 1e6
        ppm_set = set()
        charge = self.data['precursor_z'][idx]
        for isotope in range(params.MASS_ERRORS['thresholds']['isotopes']):
            ppm_set.add(ppm + isotope / (charge * params.NEUTRON_MASS))

        ends = self.query.ends
        mass = self.mass_tuple(total)
        xlname = self.xler['name']

        # grab the ms scan data for the link
        mz = self.scan_data['mz']
        intensity = self.scan_data['intensity']
        charges = self.scan_data.get('z', np.zeros(mz.size))

        link = PMFTuple(total, "fingerprint", "interlink", ppm, ppm_set,
                        ends, mass, self.ambiguous, xlname, self.xler,
                        mz, intensity, charges)
        self.matched.append(link)

    def mass_tuple(self, index):
        '''
        Returns a Mass with the ms1mass for the theoretical,
        experimental, and difference for a given peptide pair with a
        given cross-linker combination.
        '''

        # grab charge adjustments
        adjust_z = self.xler.get("delta_charge", 0)
        theor = self.calc_ms1_mass(index)
        exper = self.get_exper_mass(index)
        error = theor - exper

        return Mass(theor, exper, error, adjust_z)

    def calc_ms1_mass(self, index):
        '''
        Calculates mass of group of peptides, taking into considering
        their sequence, posttranslation modificaitons, and their neutral
        losses.
        '''

        mods = self.unpack_data('mods', index=index)
        formula = self.unpack_data('formula', index=index)
        mass = PrecursorMass(self.query.ends, self.xler, mods, formula)
        return mass['precursor']

    def get_exper_mass(self, index):
        '''Calculates the experimental MS1 mass for a given peptide.'''

        index = index[0]
        mz = self.data['precursor_mz'][index]
        charge = self.data['precursor_z'][index]
        return masstools.mz(mz, 0, charge)
