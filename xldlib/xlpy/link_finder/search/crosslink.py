'''
    XlPy/Link_Finder/search/crosslink
    _________________________________

    Identifies if a given MS3 combination masses back to an interlink,
    intralink, or deadend at one of multiple levels.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
from collections import namedtuple, Sequence

import numpy as np

from xldlib.general import sequence
from xldlib.qt.objects import base
from xldlib.resources.parameters import defaults
from xldlib.utils import logger, masstools

# CONSTANTS
# ---------
NEUTRON_MASS = 1.0033548378


# CALLABLES
# ---------

CALLABLES = [
    ("isstandardlink", "Standard"),
    ("islowconfidence", "Low Confidence"),
    ("ismultilink", "Incomplete")
]


# CHECKER
# -------


@logger.init('xlpy', 'DEBUG')
class CheckLink(base.BaseObject):
    '''
    Determines whether a given pairing is a standard, lowconfidence,
    or multilink, or none of the above.
    '''

    def __init__(self):
        super(CheckLink, self).__init__()

        self.setthresholds()

    def __call__(self, link):
        '''Check the given links name and type'''

        theoreticalcharges = link.getcharges()

        if not self._checkinvalid(link.ends):
            for funname, linkname in CALLABLES:
                fun = getattr(self, funname)
                if fun(link, theoreticalcharges):
                    return linkname

    #    SETTERS

    def setthresholds(self):
        '''Sets the scoring thresholds to validate a link object'''

        self.isotopes = defaults.DEFAULTS["isotope_threshold"]
        self.ppmthreshold = defaults.DEFAULTS["ppm_threshold"]
        self.massthreshold = defaults.DEFAULTS["mass_threshold"] / 1000

        self.minimum_peptide_mass = defaults.DEFAULTS['minimum_peptide_mass']
        self.relaxcharges = defaults.DEFAULTS['relax_charges']

    #    CHECKERS

    def isstandardlink(self, link, theoreticalcharges):
        '''
        Identifies whether a standard, high mass accuracy link occurs
        by validating it occurs within a user-defined ppm threshold.
        '''

        # check expected charge -- if fully charged out, no deal
        matchedcharge = any((
            self.relaxcharges == 'standard',
            link.scan.precursor_z in theoreticalcharges
        ))

        for isotope in range(self.isotopes):
            # add isotope shift, recalculate mass
            theoretical = link.mass.theoretical + (isotope * NEUTRON_MASS)
            ppm = link.scan.getppm(theoretical)

            link.ppm.set.add(ppm)
            if abs(ppm) < self.ppmthreshold:
                # interlink successfully identified
                # force charge matching
                if matchedcharge:
                    return True

        return False

    def islowconfidence(self, link, theoreticalcharges):
        '''
        Identifies whether a link outside the user specificed PPM window
        was identified.
        '''

        # check expected charge -- if fully charged out, no deal
        matchedcharge = any((
            self.relaxcharges == 'Low Confidence',
            link.scan.precursor_z in theoreticalcharges
        ))

        if matchedcharge:
            if abs(link.mass.error) < self.massthreshold:
                return True

        return False

    def ismultilink(self, link, theoreticalcharges):
        '''
        Checks whether a multi-link with a missing peptide
        could have been identified. Falls well outside link identification
        mass range, a range the user specifies. The mass.error is
        the theoretical - experimental mass, so this must be > threshold
        daltons (not bidirectional).
        '''

        # mass.error is theor - exper, so should be negative
        if not -link.mass.error > self.minimum_peptide_mass:
            return False

        # check expected charge -- if the precursor charge is <= than
        # all theoretical charges, impossible
        if all(i >= link.scan.precursor_z for i in theoreticalcharges):
            return False

        # must have multiple peptides and peptides must not same
        peptides = link.scan.peptide
        if len(peptides) > 1:
            if not all(i == peptides[0] for i in peptides):
                return True

        return False

    #    HELPERS

    @staticmethod
    def _checkinvalid(ends):
        '''
        Checks to ensure that all end values are above 0.
        Returns True if there is invalid (negative) data.
        :
            end -- instance of EndTuple from link_finder.crosslinks
        '''

        def negative_values(obj):
            '''Returns true if any negative ints in dictionary values'''

            return any(i < 0 for i in obj.values())

        return any(map(negative_values, (ends.link, ends.dead)))


# OBJECTS
# -------

Ppm = namedtuple("Ppm", "base set")


class LinkData(namedtuple("LinkData", "scan ends mass ppm")):
    '''Collections for crucial link parameters'''

    #    PUBLIC

    def getcharges(self):
        '''Returns the complementary, theoretical charges to form the link'''

        if isinstance(self.mass.charge, Sequence):
            charges = np.array(self.mass.charge) * self.ends.number
            return set(charges + sum(self.scan.z))
        else:
            charge = self.mass.charge * self.ends.number
            return {sum(self.scan.z) + charge}



@sequence.serializable("CrosslinkMass")
class Mass(namedtuple("Mass", "theoretical experimental error charge")):
    '''Collections for theoretical and experimental mass deviations'''


# LINK FACTORY
# ------------


@logger.init('xlpy', 'DEBUG')
class LinkFactory(base.BaseObject):
    '''Creates the link object and stores a reference'''

    def __init__(self, row, crosslinker, ends):
        super(LinkFactory, self).__init__()

        self.crosslinker = crosslinker
        self.ends = ends

        self.crosslinkedmass = masstools.CrosslinkedMass(row, crosslinker)

    def __call__(self, scan, crosslinkumber):
        '''Returns a new LinkData instance'''

        ends = self.ends(scan, crosslinkumber)
        mass = self.mass(scan, ends)
        ppm = self.ppm(mass, scan)

        return LinkData(scan, ends, mass, ppm)

    def mass(self, scan, ends):
        '''Creates a mass tuple to store mass data associated with the link'''

        theoretical = self.crosslinkedmass.getpeptidemass(
            ends, scan.formula, scan.modifications)
        experimental = scan.getmz()

        return Mass(
            theoretical,
            experimental,
            theoretical - experimental,
            self.crosslinker.charge)

    def ppm(self, mass, scan):
        return Ppm(scan.getppm(mass.theoretical), set())
