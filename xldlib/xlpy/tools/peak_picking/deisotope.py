'''
    XlPy/Tools/Peak_Picking/deisotope
    _________________________________

    Function to deisotope peaks from profile data

    :copyright: 2005-2013 Martin Strohalm <www.mmass.org>
    :modified: Alex Huszagh
    :license: GNU GPL, see licenses/mMass.txt for more details.
'''

# load future
from __future__ import division

# load modules
from xldlib.qt.objects import base
from xldlib.chemical import proteins
from xldlib.utils import logger, masstools


# CONSTANTS
# ---------

ISOTOPE_DISTANCE = 1.00287

# OBJECTS
# -------


@logger.init('peakpicking', 'DEBUG')
class Deisotope(base.BaseObject):
    '''Isotopic determination, inspired by mMass'''

    def __init__(self, peaklist, **kwds):
        super(Deisotope, self).__init__()

        self.peaklist = peaklist
        # clear previous results
        for peak in peaklist:
            peak.setcharge(None)
            peak.setisotope(None)

        min_charge = kwds.pop('min_charge', 1)
        max_charge = kwds.pop('max_charge', 5)
        self.mz_tolerance = kwds.pop('mz_tolerance', 0.10)
        self.int_tolerance = kwds.pop('int_tolerance', 0.5)
        self.isotope_shift = kwds.pop('isotope_shift', 0.0)

        # get charges
        if max_charge < 0:
            self.charges = [-x for x in range(min_charge, abs(max_charge)+1)]
        else:
            self.charges = [x for x in range(min_charge, max_charge+1)]
        self.charges.reverse()

        self.max_index = len(self.peaklist)
        self.isotopes = [None] * self.max_index

        self.deisotope()

    def deisotope(self):

        for x, parent in enumerate(self.peaklist):
            if self.isotopes[x] is not None:
                continue

            for charge in self.charges:
                cluster = self._get_cluster(x, parent, charge)

                # no isotope found
                if len(cluster) == 1:
                    continue

                # get theoretical isotopic pattern
                mass = int(masstools.mz(parent.mz, 0, charge))
                mass = min(15000, mass) // 200
                pattern = proteins.MASS_PATTERN_LOOKUP[mass]

                if self._too_few_isotopes(pattern, cluster, charge):
                    continue

                if self.valid_cluster(pattern, cluster, charge):
                    # valid ID, skip other charges
                    parent.setisotope(0)
                    parent.setcharge(charge)
                    break

    def _get_cluster(self, x, parent, charge):

        cluster = [parent]

        difference = (ISOTOPE_DISTANCE + self.isotope_shift) / abs(charge)
        y = 1
        while x + y < self.max_index:
            # tolerance should be relative to charge, updated from mMass
            mz_error = self.peaklist[x + y].mz - cluster[-1].mz - difference
            if abs(mz_error) <= self.mz_tolerance / abs(charge):
                cluster.append(self.peaklist[x + y])
            elif mz_error > self.mz_tolerance / abs(charge):
                break
            y += 1

        return cluster

    @staticmethod
    def _too_few_isotopes(pattern, cluster, charge):

        # check minimal number of isotopes in the cluster
        limit = 0
        for p in pattern:
            if p >= 0.33:
                limit += 1
        return len(cluster) < limit and abs(charge) > 1

    def valid_cluster(self, pattern, cluster, charge):

        # check peak intensities in cluster
        valid = True
        isotope = 1
        limit = min(len(pattern), len(cluster))
        while (isotope < limit):

            # calc theoretical intensity from previous peak and current error
            int_theoretical = (cluster[isotope-1].intensity /
                               pattern[isotope-1]) * pattern[isotope]
            int_error = cluster[isotope].intensity - int_theoretical

            # intensity in tolerance
            if abs(int_error) <= (int_theoretical * self.int_tolerance):
                cluster[isotope].setisotope(isotope)
                cluster[isotope].setcharge(charge)

            # intensity is higher (overlap)
            elif int_error > 0:
                pass

            # intensity is lower and first isotope is checked (nonsense)
            elif (int_error < 0 and isotope == 1):
                valid = False
                break

            # try next peak
            isotope += 1

        return valid
