'''
    Objects/Documents/Transitions/Data/charge
    _________________________________________

    Definitions for the transition document's charge level.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np

from xldlib.resources.parameters import defaults
from xldlib.utils import logger, math_, xictools

# load objects/functions
from .base import PARENT, repeat, TransitionDataBase
from .isotope import TransitionsIsotopeData


# HELPERS
# -------


def isotoperange():
    return range(defaults.DEFAULTS['quantitative_isotopes'])


# LEVEL
# -----


@logger.init('document', 'DEBUG')
class TransitionsChargeData(TransitionDataBase):
    '''Definitions for the transition charge-level data stores'''

    # KEYS
    # ----
    _child = TransitionsIsotopeData
    _children = 'isotope'
    _type = 'charge'

    def __init__(self, *args, **kwds):
        super(TransitionsChargeData, self).__init__(*args, **kwds)

    #     PUBLIC

    #    HIERARCHY

    def get_document(self):
        return repeat(PARENT, 4, self)

    def get_file(self):
        return repeat(PARENT, 3, self)

    def get_labels(self):
        return repeat(PARENT, 2, self)

    def get_crosslink(self):
        return self.parent

    def get_charge(self):
        return self

    def get_isotope(self, isotope):
        return self[isotope]

    def iter_isotope(self):
        return iter(self)

    #    SPECTRA

    def intensity(self, force_load=False):
        '''Returns the spectral intensity for the level'''

        if not force_load and self.get_document().memory:
            return self.get_labels().mem_int[self.levels]

        else:
            return self.get_file().cache.charge()[:, self.charge_index]

    def child_intensity(self, start=None, end=None, force_load=False):
        '''Returns the spectral intensity for the all children'''

        if not force_load and self.get_document().memory:
            labels = self.get_labels()
            return np.array([labels.mem_int[i.levels] for i in self])

        else:
            indexes = tuple(i.isotope_index for i in self)
            return self.get_file().cache.intensity()[start:end, indexes].T

    def get_dotp(self, bounds=None):
        '''Returns the dot product correlation between all the isotopes'''

        if bounds is None:
            start, end = self.get_crosslink().get_peak_indexes()
        else:
            start, end = bounds

        intensity = (i.intensity()[start:end] for i in self)
        monoisotopic = next(intensity)

        for isotope in intensity:
            yield math_.normalized_edge_dotp(monoisotopic, isotope)

    def get_masscorrelation(self, bounds=None, pattern=None):
        '''Mass correlation for the given crosslink. # TODO: document'''

        if bounds is None:
            start, end = self.get_crosslink().get_peak_indexes()
        else:
            start, end = bounds

        if pattern is None:
            pattern = self.get_crosslink().get_isotope_pattern()
        intensity = [i.intensity()[start:end] for i in self]
        return xictools.get_masscorrelation(intensity, pattern)

    #     METADATA

    def get_selected(self):
        return (i for i in self if i.checked)

    def update_dotp(self):
        '''Updates the dot product after peak fitting'''

        dotp = np.fromiter(self.get_dotp(), dtype=float).mean()
        self.setattr('dotp', dotp)

    #     CHILDREN

    def add_isotopes(self):
        '''Adds an isotope series to the charge holder'''

        mass = self.get_crosslink().precursor_mass
        for ion_isotope in isotoperange():
            isotope = self._child.new(self, str(ion_isotope))
            isotope.set_mass(mass)

            self.append(isotope)
