'''
    XlPy/Link_Finder/search/single
    ______________________________

    Checks if a sequenced peptide matches back to an unsequenced,
    theoretical peptide massfingerprint.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import copy

import numpy as np

from models import params
from xldlib import chemical
from xldlib.utils import iterables, masstools

# load objects/functions
from collections import namedtuple

from models.data import unpack_data
from ..crosslinks import CrossLinkerCombinations #, EndsData
from ..maker import PMFMaker
from ..objects import Ends
from xlpy.peptide_database.combinations import FragmentCombinations
from xlpy.tools.mass import PrecursorMass


class Settings(FragmentCombinations):   # EndsData
    '''Base class providing settings for inheritance'''

    max_xl = params.MASS_FINGERPRINT['max_crosslink_count']
    min_int = params.MASS_FINGERPRINT['min_intensity']
    _threshold = params.MASS_ERRORS['thresholds']["single_link"]

    ms1 = namedtuple("MS1", "ends basemass mass mz")
    query = namedtuple("Search", "ends basemass mass mz ppm exper z")
    _ppm_thresh = params.MASS_ERRORS['thresholds']['ppm'] * 1e-6

    def __init__(self):
        super(Settings, self).__init__()

        self.ms1s = []
        self.queries = []
        self.matched = []

        # apparently Windows improperly does class initiation, have
        # to manually __get__ to class instance.
        self.unpack_data = unpack_data.__get__(self)
        self.calculate_mass = PrecursorMass.calculate_mass.__get__(self)
        self.get_exper_mass_ = PMFMaker.get_exper_mass.__get__(self)


class PMFChecker(Settings):
    '''
    Class which checks possible crosslinker and deadend combinations
    after calculating the theoretical profile and then determines
    if any matches can be found.
    '''

    def __init__(self, scan, indexer, index, parent):
        super(PMFChecker, self).__init__()

        # here, need to recalculate the number of possible XL
        # number based on the fragments with 2 peptides
        self.scan = copy.deepcopy(scan)
        self.formula = self.scan.formula
        self.parent = parent
        self.xler = parent.xler
        self.data = parent.data

        self._nterm = parent.engine['nterm']
        self._cterm = parent.engine['cterm']

        self.bridge = chemical.Molecule(self.parent.xler['bridge']).mass()
        self.fragment_masses = self.get_fragment_masses()
        self.site_mass = self.get_sitemass()
        self.index = [indexer.total[index]]

        self.scan_data = self.get_scan_data()
        self.mz = self.scan_data['mz'].value
        self.intensity = self.scan_data['intensity'].value

        self.xlnum = None
        self.theor_charge = None
        self.link_ends_base = self.get_link_ends()
        self.order = sorted(set(self.xler['react_sites']))

    def check_single(self):
        '''
        Checks a single to identify if any other sequences are possible
        Does this via a sequential procedure.
            1. Calculates all possible permutations of the other peptides
                crosslinker combinations.
            2. Iterates over all possibilities to calculate the basemass
                to generate a potential mass list.
            3. Filter only for transitions with an identified mass in
                the m/z list.
        '''

        # can skip peptide since only one index passed in...
        if self.missing_z() <= 0 or self.check_threshold():
            return
        other_fragments = self.get_other_fragment()
        self.iter_fragments(other_fragments)
        self.extract_mzs()
        # minimize memory usage
        del self.mz
        del self.intensity
        self.search()

    def check_threshold(self):
        '''
        Calculates mass of group of peptides, taking into considering
        their sequence, posttranslation modificaitons, and their neutral
        losses.
        '''

        formulas = self.unpack_data('formula')
        theor = sum(chemical.Molecule(i).mass for i in formulas)
        exper = self.get_exper_mass_(self.index)

        return exper - theor < self._threshold

    # ------------------
    #      STEP 1
    # ------------------

    def get_other_fragment(self):
        '''
        Calculates all permutations of the other peptide's crosslink
        fragments, so that the XL numbers can then be iterated over.
        '''

        fragments = [range(0, self.max_xl + 1) for i in self.order]
        return iterables.num_product(*fragments, min=1, max=self.max_xl)

    # ------------------
    #      STEP 2
    # ------------------

    def iter_fragments(self, other_fragments):
        '''
        Step 2 in the check_single algorithm, which iterates over all
        the crosslink fragment options and then calculates the total,
        intact XL num and calculates the MS2 mass options.
        '''

        for fragments in other_fragments:
            link_ends = self.get_combo_linkends(fragments)
            combinations = CrossLinkerCombinations(
                self.scan, self, missing=1, fragments=link_ends)

            for self.xlnum in combinations:
                adjust_z = self.parent.xler.get('delta_charge', 0)
                self.theor_charge = sum(self.scan.z) + adjust_z * self.xlnum

                try:
                    ms1 = self.get_missing_mass(link_ends, fragments)
                    self.ms1s.append(ms1)
                except AssertionError:
                    pass

    def get_combo_linkends(self, fragments):
        '''Grabs the linkends for a given other fragment set'''

        link_ends = self.link_ends_base.copy()
        for index, res in enumerate(self.order):
            link_ends[res] += fragments[index]
        return link_ends

    def get_missing_mass(self, link_ends, fragments):
        '''
        Grabs the missing basemass and initiates a named tuple for
        the mass lists form the link and deadends.
        '''

        max_links = self.max_link_ends()
        dead_ends = self.get_dead_ends(link_ends, max_links)
        ends = Ends(link_ends, dead_ends, self.xlnum)

        # now need to calculate the base mass and mass permutations
        basemass = self.missing_ms1_mass(dead_ends)
        assert basemass > self._threshold
        mass_perm = list(self.get_fragment_combinations(sum(fragments), False))

        mzs = []
        for mass in mass_perm:
            mz_ = masstools.mz(basemass + sum(mass), self.missing_z(), 0)
            mzs.append(mz_)
        mzs = np.array(mzs).reshape((-1, 1))
        ms1 = self.ms1(ends, basemass, mass_perm, mzs)

        return ms1

    def missing_ms1_mass(self, dead_ends):
        '''
        Calculates the MS1 mass and linkmass and then compares to the
        experimental MS1 mass to find the missing MS1 mass.
        '''

        linkmass = self.xlnum * self.bridge
        for res, count in dead_ends.items():
            linkmass += self.site_mass[res] * count

        basemass = self.calculate_mass()
        theor = linkmass + basemass
        exper = self.get_exper_mass()
        return exper - theor

    # ------------------
    #      STEP 3
    # ------------------

    def extract_mzs(self):
        '''
        Step 3 in the sequence. This extracts all the m/z values from
        the given candidate list within the ppm  threshold for each
        candidate fragment modification possibilities.
        '''

        mzs = [ms1.mz for ms1 in self.ms1s]
        ppms = [abs(self.mz - _mz) / _mz for _mz in mzs]
        entries, indexes = self.extract_indexes(ppms)
        if not indexes:
            return

        filt_other = [self.ms1s[index] for index in indexes]
        filt_entries = [entries[index] for index in indexes]
        filt_ppms = [ppms[index] for index in indexes]

        for index, other in enumerate(filt_other):
            # need to filter for a certain pct basepeak
            rows, cols = filt_entries[index]
            ppm = filt_ppms[index]
            self.pack_searchable(ppm, other, rows, cols)

    def pack_searchable(self, ppm, other, rows, cols):
        '''Packs the searchable MS transition for peptide mass fingerprint'''

        ppm_list = self.get_ppms(ppm, rows, cols)
        mz_ = other.mz[rows].flatten()
        mass = tuple(other.mass[row] for row in rows)
        exper = self.mz[cols]

        query = self.query(other.ends, other.basemass, mass, mz_,
                           ppm_list, exper, self.missing_z())
        self.queries.append(query)

    # ------------------
    #      STEP 4
    # ------------------

    def search(self):
        '''
        Step 4 in the search algorithm, by comparing to a theoretical DB.
        Searches for all matched transitions, including decoys if on,
        first by combining the decoy and standard dbs, creating a search
        param and then comparing theoretical to experimental.
        '''

        for query in self.queries:
            mass_keys = [str(i) for i in query.mass]
            for index, mass_key in enumerate(mass_keys):
                items = self.get_theoretical(mass_key)
                if not items:
                    continue
                self.search_items(query, items, index)


    def get_theoretical(self, mass_key):
        '''Extracts the theoretical peptide databases for searching'''

        items = []
        for database in self.parent.dbs:
            if mass_key in self.parent.searchables[database]:
                items.append(self.parent.searchables[database][mass_key])

        return items

    def search_items(self, query, items, index):
        '''Generates a search query for the given peptide items'''

        search = {}
        length = items[0]['id'].shape[0]
        for database in items:
            for idx in range(length):
                search = {k: database[k][idx] for k in database}
                PMFMaker(query, search, index, self, self.parent)

    # ------------------
    #      UTILS
    # ------------------

    def get_scan_data(self):
        '''Returns the MS2 scan data for link'''

        precursor = self.data['precursor_num'][self.index[0]]
        scan_data = self.parent.precursor_scans[str(precursor)]

        return scan_data

    def get_sitemass(self):
        '''Creates a {res: mass} holder for deadend mods'''

        dead = self.xler['dead_end']
        react = self.xler["react_sites"]
        sitemass = {res: chemical.Molecule(dead[i]).mass for i, res
                    in enumerate(react)}

        return sitemass

    def missing_z(self):
        '''Calculates the theoretical missing peptide charge'''

        if self.theor_charge is None:
            # assume 1 XLer mod
            adjust_z = self.xler.get('delta_charge', 0)
            charges = sum(self.unpack_data("z"))
            return self.scan.precursor_z - charges - adjust_z
        else:
            return self.scan.precursor_z - self.theor_charge

    def extract_indexes(self, ppms):
        '''
        Extracts all the XL-MS indexes within the default ppm threshold
        of the desired ID and those above a certain percentage of basepeak
        '''

        try:
            basepeak = self.intensity.max()
            ints = self.intensity >= basepeak * self.min_int
        except ValueError:
            # no scan data
            return [], []

        entries = [np.where((ppm <= self._ppm_thresh) & ints) for ppm in ppms]
        indexes = [i for i, j in enumerate(entries) if j[0].size > 0]

        return entries, indexes

    @staticmethod
    def get_ppms(ppm_array, rows, cols):
        '''Returns the experimental PPMs within the parent threshold'''

        ppm_list = []
        indexes = zip(rows, cols)
        for index in indexes:
            # has a zipped (row, col) format for single indexing,
            # which is much faster than chained or ndarray.item()
            ppm_list.append(ppm_array[index])
        return ppm_list
