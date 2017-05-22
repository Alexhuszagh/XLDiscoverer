'''
    XlPy/Peptide_Database/core
    __________________________

    Generates a searchable series of NumPy arrays oranized by the number
    of missed cleavages.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from models import params
from xldlib.definitions import re
from xldlib.objects.abstract import mapping
from xldlib.utils.conn import uniprot

# load objects/functions
from collections import defaultdict

from .enzyme import CutSites
from .hdf5 import HDF5Utils
from .mods import AddMods

# ------------------
#    PEPTIDE DB
# ------------------


class PeptideDBSettings(mapping.MethodlessCopyDict):
    '''Provides a base class for settings for the called class'''

    def __init__(self):
        super(PeptideDBSettings, self).__init__()

        self.max_xl = params.MASS_FINGERPRINT['max_crosslink_count']
        self.max_mods = params.MASS_FINGERPRINT['max_mods']
        self.max_missed = params.MASS_FINGERPRINT['max_missed_cleavages']
        self.min_length = params.MASS_FINGERPRINT['min_length']
        self.max_length = params.MASS_FINGERPRINT['max_length']
        self.consistent_decoys = params.MASS_FINGERPRINT['consistent_decoys']
        self.nonspecific = params.MASS_FINGERPRINT['nonspecific']['current']

        self.peptide_dtype = 'S{}'.format(self.max_length)
        self.formula_dtype = 'S20'


class PeptideDatabase(PeptideDBSettings, CutSites, AddMods, HDF5Utils):
    '''
    Creates a custom peptide database with various settings from 1- max
    crosslinker modifications for each permutation, and the number of
    mods up to the max (with XL mods) defined by the search.
    '''

    db_modes = {True: {'standard', 'decoy'}, False: {'standard'}}
    peptides = None
    searchables = None
    mods_length = None
    modifications_dtype = None
    mod_ids = None
    _mode = None

    id_regex = re.compile(uniprot.SERVER['id']['regex'], re.IGNORECASE)
    entry_regex = re.compile(uniprot.SERVER['entry']['regex'], re.IGNORECASE)

    def __init__(self, grp, xler, source):
        super(PeptideDatabase, self).__init__()

        self.grp = grp
        self.xler = xler
        self.source = source
        self.mods = params.CUSTOM_MODS
        self.react = set(self.xler['react_sites'])
        # default to true, newly set value
        self.uncleaved = self.xler.get("uncleaved", True)
        self.fragment_masses = self.get_fragment_masses()
        self.basemods = self.organize_basemods()
        self._set_mod_ids()

        self.sequences = self._get_sequences()

        self.decoy = params.MASS_FINGERPRINT['search_decoys']
        self._peptide_holders()

        self.run()

    def run(self):
        '''On start'''

        self._mode = 'standard'
        self.add_ids()
        self.make_searchables()
        if self.decoy:
            self._mode = 'decoy'
            self.make_searchables()

        for key in {'base_peptides', 'peptides'}:
            del self.grp[key]
        self.linearize()

    # ------------------
    #       PUBLIC
    # ------------------

    def add_ids(self):
        '''Adds a way to map the sequence ids to the current holder'''

        ids = [i.encode('utf-8') for i in self.sequences]
        self.grp.attrs.create('protein_ids', data=ids)
        names = [i.name.encode('utf-8') for i in self.sequences.values()]
        self.grp.attrs.create('protein_names', data=names)

    def make_searchables(self):
        '''On start'''

        self.cut_sequences()
        self.add_mods()

    # ------------------
    #   PRIVATE -- INIT
    # ------------------

    def _get_sequences(self):
        '''Updates sequence dictionary with entries from the limited db'''

        sequences = {}
        limited_db = self.source.limited_database
        for id_ in limited_db:
            if id_ in self.source.custom_proteins:
                sequences[id_] = self.source.custom_proteins[id_]
            elif id_ in self.source.gene_name:
                sequences[id_] = self.source.gene_name[id_]

        return sequences

    def _peptide_holders(self):
        '''Adds peptide holders for later stimulated cutting'''

        for key in {'base_peptides', 'decoy', 'standard'}:
            self.grp.create_group(key)

        peptides = self.grp.create_group('peptides')
        db_keys = self.db_modes[self.decoy]
        for key in db_keys:
            for missed_cleavages in range(self.max_missed + 1):
                peptides.create_group('{}/{}'.format(key, missed_cleavages))

        # temporary, fast data holder for in memory searchables
        self.searchables = {}
        for key in db_keys:
            self.searchables[key] = defaultdict(list)

    def _set_mod_ids(self):
        '''
        Assigns unique mod ids for each modification and stores a copy
        in the dataset.
        '''

        names = [i[0] for item in self.basemods.values() for i in item]
        names += self.xler['fragments']['name']
        # grabs the number of places required to store data
        self.mods_length = (len(names) // 10) + 1
        # +2 for n and c-term
        max_mods = self.mods_length * self.max_length + 2
        self.modifications_dtype = 'S{}'.format(max_mods)

        self.mod_ids = {}
        for index, name in enumerate(names):
            self.mod_ids[name] = index

        # store as attrs to unpack later
        self.grp.attrs.create('modification_ids', data=range(len(names)))
        bin_names = [i.encode('utf-8') for i in names]
        self.grp.attrs.create('modification', data=bin_names)
