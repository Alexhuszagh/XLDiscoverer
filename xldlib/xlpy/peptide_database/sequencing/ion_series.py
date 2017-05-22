'''
    XlPy/Peptide_Database/Sequencing/ion_series
    ___________________________________________

    Generates theoretical ion fragmentation series for peptide
    sequencing ion matching.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import numpy as np

from models import params

from xldlib import chemical
from xldlib.resources import chemical_defs, parameters
from xldlib.utils import masstools

# load objects/functions
from operator import iadd, isub

# CONSTANTS
# ---------

WATER_MASS = chemical.Molecule(params.WATER_FORMULA).mass


# SERIES
# ------


class IonSeries(object):
    '''Generates an ion series for peptide searching'''

    _params = parameters.INSTRUMENTS
    _aminoacids = chemical_defs.AMINOACIDS

    def __init__(self, peptide, charge, mode):
        '''
        Generates the ion series, with the mode being in:
        {'a', 'an', 'ao', 'b', 'bn', 'bo', 'c', 'd', 'v', 'w', 'x',
         'y', 'yn', 'yo', 'z'}
        '''
        super(IonSeries, self).__init__()

        self.peptide = peptide
        self.length = len(peptide)
        self.mode = mode
        # probably a given constant number, so can be convulted to "mods"
        self.constant_mods = {}
        self.variable_mods = {}

        self.instrument = parameters.INSTRUMENTS[parameters.CURRENT_INSTRUMENT]
        self._charges = [i for i in self.instrument.charges if i <= charge]

        self.mzs = []
        self.charges = []
        self.position = []

        self.ion_series = getattr(self, "_{}_series".format(self.mode))

    # ------------------
    #     IMMONIUM
    # ------------------

    def immonium(self):
        '''Provides the immonium ion for the N-terminus'''

        for residue in set(self.peptide):
            mass = (chemical.Molecule(residue).mass -
                    chemical.Molecule('C O H-1').mass)

    # ------------------
    #  SPECIFIC SERIES
    # ------------------

    # TODO: Add mods to each calculation

    #     A SERIES

    def _a_series(self):
        '''
        Related to the b-ion series, which is characterized by [N]+[M]-CHO,
        differing slightly from the [N]+[M]-H from the N-terminus.
        For example, the b3 ion for KPIDWGAASPAVQSFR is the mass of
        KPI  - CHO + # proton(s) * charge.
        '''

        self._b_series()
        self._neutralchange('C O')

    def _an_series(self):
        '''a series with an NH3 loss'''

        self._a_series()
        self._neutralchange('N H3')

    def _ao_series(self):
        '''a series with an H2O loss'''

        self._a_series()
        self._neutralchange('H2 O')

    #     B SERIES

    def _b_series(self):
        '''
        Calculates the b-ion series, which is characterized by the following
        formula: [N]+[M]-H, starting from the N-terminus.
        For example, the b3 ion for KPIDWGAASPAVQSFR is the mass of
        KPI + # proton(s) * charge.
        '''

        for position in range(2, self.length):
            for charge in self._charges:
                seq = self.peptide[:position]
                mass = (chemical.Molecule(self._aminoacids[i]) for i in seq)
                mass = (i.mass for i in mass)
                mz = masstools.mz(mass, charge, 0)

                self.mzs.append(mz)
                self.charges.append(charge)
                self.position.append(position)

        self._toarray()

    def _bn_series(self):
        '''b series with an NH3 loss'''

        self._b_series()
        self._neutralchange('N H3')

    def _bo_series(self):
        '''b series with an NH3 loss'''

        self._b_series()
        self._neutralchange('H2 O')

    #     C SERIES

    def _c_series(self):
        '''
        Calculates the c-ion series, which is characterized by the following
        formula: [N]+[M]+NH2, starting from the N-terminus.
        For example, the c3 ion for KPIDWGAASPAVQSFR is the mass of
        b ion series + NH3.
        '''

        self._b_series()
        self._neutralchange('N H3', fun=iadd)


    #     D SERIES

    def _da_series(self):
        pass

    def _db_series(self):
        pass

    #     V SERIES

    def _v_series(self):
        pass

    #     W SERIES

    def _wa_series(self):
        pass

    def _wb_series(self):
        pass

    #     X SERIES


    def _x_series(self):
        '''
        Calculates the x-ion series, which is characterized by the following
        formula: [C]+[M]+ CO-H, starting from the C-terminus.
        For example, the x3 ion for KPIDWGAASPAVQSFR is the mass of
        y ion series + CO - H.
        '''

        self._y_series()
        self._neutralchange('C O H-2', fun=iadd)

    #     Y SERIES

    def _y_series(self):
        '''
        Calculates the y-ion series, which is characterized by the following
        formula: [C]+[M]+H, starting from the C-terminus.
        For example, the y3 ion for KPIDWGAASPAVQSFR is the mass of
        SFR + water + # proton(s) * charge.
        '''

        for position in range(1, self.length):
            for charge in self._charges:
                seq = self.peptide[-position:]
                mass = sum(chemical.Molecule(self._aminoacids[i]) for i in seq)
                mass = (i.mass for i in mass)
                mass += WATER_MASS
                mz = masstools.mz(mass, charge, 0)

                self.mzs.append(mz)
                self.charges.append(charge)
                self.position.append(position)

        self._toarray()

    def _yn_series(self):
        '''b series with an NH3 loss'''

        self._y_series()
        self._neutralchange('N H3')

    def _yo_series(self):
        '''b series with an NH3 loss'''

        self._y_series()
        self._neutralchange('H2 O')

    #     Z SERIES

    def _z_series(self):
        '''
        Calculates the z-ion series, which is characterized by the following
        formula: [C]+[M]-NH2, starting from the C-terminus.
        For example, the z3 ion for KPIDWGAASPAVQSFR is the mass of
        y ion series - NH2.
        '''

        self._y_series()
        self._neutralchange('N H2')

    # ------------------
    #     SUBSERIES
    # ------------------

    def _neutralchange(self, formula, fun=isub):
        '''Substracts a given neutral loss from the mz list'''

        fun(self.mzs, chemical.Molecule(formula).mass / self.charges)

    # ------------------
    #      AS ARRAY
    # ------------------

    def _toarray(self):
        '''Converts the mz, charge and position lists to arrays'''

        for key in ["mzs", "charges", "position"]:
            setattr(self, key, np.array(getattr(self, key)))
