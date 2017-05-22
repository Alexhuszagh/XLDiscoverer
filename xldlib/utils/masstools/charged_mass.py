'''
    Utils/Masstools/charged_mass
    ____________________________

    Tools for calculating mass to charge (m/z) ratios and mass error
    (in ppm).

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# CONSTANTS
# ---------
PROTON_MASS = 1.00727647
PPM_SCALAR = 1e6


# MASS-TO-CHARGE
# --------------


def mz(mass, final_charge, initial_charge=0):
    '''
    Calculate the m/z, or mass-to-charge value, for a given ion:
        mass (float):           mass of the given item
        final_charge (int):     final charge of the ion
        initial_charge (int):   initial_charge of the ion
    '''

    if initial_charge != 0:
        mass = (mass * initial_charge) - (PROTON_MASS * initial_charge)

    if final_charge != 0:
        mass = (mass + (PROTON_MASS * final_charge)) / final_charge

    return mass


def ppm(experimental_mass, experimental_z, theoretical_mass, theoretical_z=0):
    '''
    Calculate ppm between the experimental and the theoretical mass
    based on the mass/charge ratio (m/z) at the experimental charge.
        experimental_mass (float): mass of the experimental ion at charge
        experimental_z (int):      experimental charge
        theoretical_mass (float):  mass of the theoretical ion at charge
        theoretical_z (int):       charge of the theoretical ion
    '''

    theoretical_mz = mz(theoretical_mass, experimental_z, theoretical_z)
    return (experimental_mass - theoretical_mz) * PPM_SCALAR / theoretical_mz


