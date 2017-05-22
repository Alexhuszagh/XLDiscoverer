'''
    Utils/Masstools/formula
    _______________________

    Tools for calculating theoretical peptide formulas and masses.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import print_function

# load modules
import sys

from xldlib import chemical
from xldlib.definitions import ZIP
from xldlib.resources import chemical_defs
from xldlib.utils import logger


__all__ = [
    'CrosslinkedMass',
    'getpeptideformula',
]


# STANDARD PEPTIDES
# -----------------


def add_modifications(self, *ids, **kwds):
    '''
    Add modifications from `ids` to `self`, calling `update_formula`
    to add the new elements.

    Args:
        ids (int):  integer IDs for the modifications
    Kwds:
        crosslinkers (bool):   include crosslinker framgents (False)
    '''

    mods = (chemical_defs.MODIFICATIONS[i] for i in ids)
    filtered = (i for i in mods if kwds.get('crosslinkers') or not i.fragment)
    for modification in filtered:
        self.update_formula(formula=modification.formula)


#def add_modifications(modificationids, atomcounts, with_crosslinkers):
#    '''Adds modification formulas to the current chemical.Molecule inst'''
#
#    for modification_id in modificationids:
#        db_modification = chemical_defs.MODIFICATIONS[modification_id]
#        if with_crosslinkers or not db_modification.fragment:
#            atomcounts.update_formula(formula=db_modification.formula)


def getmodificationsformula(modifications, engine, **kwds):
    '''
    Calculates formula for all mods within standard library,
    potentially including chemical crosslinker fragments if
    with_crosslinkers is set to True.
    '''

    atom_counts = chemical.Molecule()
    modifications = modifications.byposition()

    for position, names in modifications.items():
        try:
            if frozenset(names) in chemical_defs.MODIFICATION_INTERACTIONS:
                # add the converted modification from id
                id_ = chemical_defs.MODIFICATION_INTERACTIONS[names].converted
                add_modifications(atom_counts, id_, **kwds)
            else:
                # no modification interaction, just add
                #ids = (engine.defaults.modifications.get(i)[0] for i in names)
                ids = [engine.defaults.modifications.get(i)[0] for i in names]
                add_modifications(atom_counts, *ids, **kwds)

        except (TypeError, IndexError):
            # Nonetype from .get(name)[0] or [][0]
            print("Modification not recognized: " + str(names), file=sys.stderr)

    return atom_counts


def getpeptideformula(peptide, mods, engine, **kwds):
    '''
    Returns the full mass for the peptide, with modifications, assuming
    by default only modifications in the standard library.
    '''

    atomcounts = getmodificationsformula(mods, engine, **kwds)
    atomcounts.update_formula(peptide=peptide)

    return atomcounts


# CROSSLINKED PEPTIDES
# --------------------


@logger.init('chemical', 'DEBUG')
class CrosslinkedMass(object):
    '''
    Definitions for finding crosslinker link masses and crosslinked peptide
    masses.
    '''

    def __init__(self, row, crosslinker):
        super(CrosslinkedMass, self).__init__()

        self.crosslinker = crosslinker
        self.engine = row.engines['matched']

        self.setdeadendmass(crosslinker.ends)
        self.bridgemass = chemical.Molecule(crosslinker.bridge).mass

    #     SETTERS

    def setdeadendmass(self, ends):
        '''
        Sets the mass for each deadend modificiation on a crosslinker at
        each reactive site, allowing quick lookups.
        '''

        zipped = ZIP(ends.aminoacid, ends.deadend)
        self.deadendmass = {r: chemical.Molecule(d).mass for r, d in zipped}

    #     GETTERS

    def getpeptidemass(self, ends, formulas, modifications):
        '''Returns the total mass for a crosslinked peptide'''

        masses = (i.mass for i in formulas)
        neutrallosses = (i['neutralloss'] for i in modifications)

        return sum(masses) + sum(neutrallosses) + self.getlinkmass(ends)

    def getlinkmass(self, ends):
        '''Calculates the linkmass of the crosslinked peptide bridging mode'''

        deadend = self.getdeadendmass(ends)
        return sum(deadend) + (ends.number * self.bridgemass)

    def getdeadendmass(self, ends):
        '''Calculates the mass changes from each deadend modification.'''

        for reactivity, count in ends.dead.items():
            yield self.deadendmass[reactivity] * count
