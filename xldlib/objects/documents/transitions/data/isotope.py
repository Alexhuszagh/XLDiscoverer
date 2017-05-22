'''
    Objects/Documents/Transitions/Data/isotope
    __________________________________________

    Definitions for the transition document's isotope level.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np

from xldlib.utils import logger, masstools, math_, xictools

# load objects/functions
from .base import PARENT, repeat, TransitionDataBase


# CONSTANTS
# ---------
# Based on the PM-rule, specified in PMID: 10612279
#   Similar isotope distance is used in OpenMS
#   mMass uses a slightly different value at 1.00287
ISOTOPE_DISTANCE = 1.000495


# LEVEL
# -----


@logger.init('document', 'DEBUG')
class TransitionsIsotopeData(TransitionDataBase):
    '''Definitions for the transition isotope-level data stores'''

    # KEYS
    # ----
    _child = None
    _children = None
    _type = 'isotope'

    # ROUNDING
    # --------
    precision = 4

    def __init__(self, *args, **kwds):
        super(TransitionsIsotopeData, self).__init__(*args, **kwds)

        self.isotope = int(self.levels.isotope)
        self.charge = int(self.levels.charge)

    #    HIERARCHY

    def get_document(self):
        return repeat(PARENT, 5, self)

    def get_file(self):
        return repeat(PARENT, 4, self)

    def get_labels(self):
        return repeat(PARENT, 3, self)

    def get_crosslink(self):
        return repeat(PARENT, 2, self)

    def get_charge(self):
        return self.parent

    def get_isotope(self, isotope):
        return self

    #    SPECTRA

    def round(self):
        return round(self.isotope_mz, self.precision)

    def intensity(self, force_load=False):
        '''Returns the spectral intensity for the level'''

        if not force_load and self.get_document().memory:
            return self.get_labels().mem_int[self.levels]

        else:
            return self.get_file().cache.intensity()[:, self.isotope_index]

    def mz(self, force_load=False):
        '''Returns the spectral m/z for the level'''

        if not force_load and self.get_document().memory:
            return self.get_labels().mem_mz[self.levels]

        else:
            return self.get_file().cache.mz()[:, self.isotope_index]

    def get_gaussian(self, bounds=None):
        '''Returns the gaussian correlation of the current peak'''

        if bounds is None:
            start, end = self.get_crosslink().get_peak_indexes()
        else:
            start, end = bounds

        x = self.get_retentiontime(start-1, end+1)
        y = np.r_[0, self.intensity()[start:end], 0]

        return math_.fit_gaussian(x, y)

    def get_ppm(self, *args, **kwds):
        return xictools.get_isotopeppm(self, *args, **kwds)

    #    METADATA

    def update_gaussian(self):
        self.setattr('gaussian', self.get_gaussian())

    def ischecked(self):
        return (self.checked &
            self.get_charge().checked &
            self.get_crosslink().checked)

    #    SETTERS

    def set_mass(self, monoisotopic):
        '''Sets the isotopic mass for XICs and then adds self to flattened'''

        mass = monoisotopic + (ISOTOPE_DISTANCE * self.isotope)
        self.setattr('isotope_mass', mass)

        mz = masstools.mz(mass, self.charge, 0)
        self.setattr('isotope_mz', mz)
