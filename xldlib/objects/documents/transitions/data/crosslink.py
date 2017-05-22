'''
    Objects/Documents/Transitions/Data/crosslink
    ____________________________________________

    Definitions for the transition document's crosslink level.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import itertools as it

import numpy as np

from xldlib.chemical import proteins
from xldlib.resources.parameters import defaults
from xldlib.utils import logger, xictools

# load objects/functions
from .base import LinearRange, PARENT, repeat, TransitionDataBase
from .charge import TransitionsChargeData


# HELPERS
# -------


def chargerange(charge):
    '''Expands the target charge for a selection range'''

    if defaults.DEFAULTS['expand_charges']:
        # expand the charge search to a given range (usually +/- 1)
        return range(
            charge - defaults.DEFAULTS['minus_charge_range'],
            charge + defaults.DEFAULTS['plus_charge_charge'] + 1,
        )
    else:
        # keep only the current charge
        return [charge]


# LEVEL
# -----


@logger.init('document', 'DEBUG')
class TransitionsCrosslinkData(TransitionDataBase):
    '''Definitions for the transition crosslink-level data stores'''

    # KEYS
    # ----
    _child = TransitionsChargeData
    _children = 'charge'
    _type = 'crosslink'

    def __init__(self, *args, **kwds):
        super(TransitionsCrosslinkData, self).__init__(*args, **kwds)

    #     PUBLIC

    #    HIERARCHY

    def get_document(self):
        return repeat(PARENT, 3, self)

    def get_file(self):
        return repeat(PARENT, 2, self)

    def get_labels(self):
        return self.parent

    def get_crosslink(self):
        return self

    def get_charge(self, charge):
        return self[charge]

    def get_isotope(self, charge, isotope):
        return self[charge][isotope]

    def iter_charge(self):
        return iter(self)

    def iter_isotope(self):
        return it.chain.from_iterable(self)

    #    SPECTRA

    def intensity(self, force_load=False):
        '''Returns the spectral intensity for the level'''

        if not force_load and self.get_document().memory:
            return self.get_labels().mem_int[self.levels]

        else:
            return self.get_file().cache.crosslink()[:, self.crosslink_index]

    def child_intensity(self, start=None, end=None, force_load=False):
        '''Returns the spectral intensity for the all children'''

        if not force_load and self.get_document().memory:
            labels = self.get_labels()
            return np.array([labels.mem_int[i.levels] for i in self])

        else:
            indexes = tuple(i.charge_index for i in self)
            return self.get_file().cache.charge()[start:end, indexes].T

    def charge_intensity(self, charges, start=None, end=None):
        indexes = tuple(i.charge_index for i in charges)
        return self.get_file().cache.charge()[start:end, indexes].T

    def isotope_intensity(self, charges, start=None, end=None):
        for charge in charges:
            indexes = tuple(i.isotope_index for i in charge)
            yield self.get_file().cache.intensity()[start:end, indexes].T

    def integrate_data(self, charges=()):
        return xictools.xic_data(self, charges)

    def calculate_fit(self):
        '''
        Post-fitting calculations to assess the fit quality for each charge
        and isotope, both through Gaussian and dot product correlations.
        '''

        for charge in self:
            charge.update_dotp()
            for isotope in charge:
                isotope.update_gaussian()

    #     PEAK

    def get_relative_peak_index(self, key):
        '''Gets an HDF5 attribute for the peak indexes'''

        key = 'peak_' + key
        if hasattr(self, key):
            return getattr(self, key)
        else:
            return getattr(self.get_labels(), key)

    def get_peak_indexes(self):
        return LinearRange(self.get_start_index(), self.get_end_index())

    def get_peak_bounds(self):
        rt = self.get_retentiontime()
        peak = self.get_peak_indexes()
        return LinearRange(rt[peak.start], rt[peak.end])

    def get_start_index(self):
        '''Returns the start index for the peak within the full chromatogram'''

        labels = self.get_labels()
        window_start = labels.window_start
        if hasattr(self, 'peak_start'):
            peak_start = self.peak_start
        else:
            peak_start = labels.peak_start

        return window_start + peak_start

    def get_end_index(self):
        '''Returns the end index for the peak within the full chromatogram'''

        labels = self.get_labels()
        window_start = labels.window_start
        if hasattr(self, 'peak_end'):
            peak_end = self.peak_end
        else:
            peak_end = labels.peak_end

        return window_start + peak_end

    #   METADATA

    def get_selected(self):
        return (i for i in self if i.checked)

    def get_sequencedcharges(self):
        '''Returns the charge items corresponding to sequenced IDs'''

        precursors = set(self.get_labels().precursor_z)
        return [self.get_charge(str(i)) for i in precursors]

    def get_checkedcharges(self):
        return ', '.join([str(i.levels.charge) for i in self.get_selected()])

    def get_ppm(self, start=None, end=None):
        '''Wrapper with typechecker for xictools.get_ppm'''

        if start is None or end is None:
            start, end = self.get_peak_indexes()
        return xictools.get_ppm(self, start, end)

    def get_dotp(self, bounds=None):
        dotps = (i.get_dotp(bounds) for i in self.get_selected())
        return np.mean([i for item in dotps for i in item])

    def get_header(self):
        profile = self.get_document().profile
        return profile.getheader(self.populations)

    def get_fitscore(self):
        return xictools.scorecrosslink(self)

    def get_baseline(self):
        return np.median(self.intensity())

    def get_noise(self):
        return np.std(self.intensity())

    def get_masscorrelation(self):
        '''Isotope mass correlation between experimental and thereetical'''

        charges = self.get_selected()
        start, end = self.get_peak_indexes()

        generator = self.isotope_intensity(charges)
        isotopes = [[i[start:end] for i in item] for item in generator]
        pattern = self.get_isotope_pattern()
        corr = [xictools.get_masscorrelation(i, pattern) for i in isotopes]
        return np.mean(corr)

    def get_isotope_pattern(self):
        '''Returns the predicted, theoretical isotope pattern'''

        binned_mass = int(self.precursor_mass // 200)
        isotope_pattern = proteins.MASS_PATTERN_LOOKUP[binned_mass]
        isotopes = defaults.DEFAULTS['quantitative_isotopes']
        return isotope_pattern[:isotopes]

    #   CHILDREN

    def add_charge(self, ion_charge, mass):
        '''Adds a single charge to the current group'''

        ion_charge = str(ion_charge)
        if not self.has_key(ion_charge):
            charge = self._child.new(self, ion_charge)
            self.append(charge)
            charge.add_isotopes()

    #    SETTERS
    #      NEW

    def set_crosslink(self, label):
        '''Initializes the parameters and children from a crosslink level'''

        self.setattr('modifications', label.modifications)
        self.setattr('populations', label.populations)
        self.setattr('precursor_mass', label.mass)
        self.setattr('delta_retentiontime', 0.)

    def set_charges(self, label, precursor_z):
        for charge in chargerange(precursor_z):
            self.add_charge(charge, label.mass)

    #     PEAK

    def set_peak_index(self, key, index):
        '''Sets an HDF5 attribute for the peak indexes'''

        key = 'peak_' + key
        if hasattr(self, key):
            self.setattr(key, index)
        else:
            self.get_labels().setattr(key, index)

    def set_peak_indexes(self, start, end):
        self.set_peak_index('start', start)
        self.set_peak_index('end', end)
