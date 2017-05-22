'''
    Resources/Parameters/instruments
    ________________________________

    Instrument definitions for sequencing ions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import six

from collections import namedtuple

from xldlib.general import sequence

# OBJECTS
# -------


@sequence.serializable("DeltaFormulaIon")
class DeltaFormulaIon(namedtuple("DeltaFormulaIon", "name "
    "letter formula residues")):

    def __new__(cls, name, letter, formula, residues):
        if isinstance(residues, six.string_types):
            residues = set(residues.split(','))

        return super(DeltaFormulaIon, cls).__new__(cls, name,
            letter, formula, residues)


@sequence.serializable("SequencingIon")
class SequencingIon(namedtuple("SequencingIon", "series terminus "
    "formula z loss addition")):

    def __new__(cls, series, terminus, formula="", z=0,
        loss=None, addition=None):
        if loss is None:
            loss = []

        if addition is None:
            addition = []

        return super(SequencingIon, cls).__new__(cls, series,
            terminus, formula, z, loss, addition)


@sequence.serializable("Instrument")
class Instrument(namedtuple("Instrument", "name charges "
    "min_internal_mass max_internal_mass ions")):

    def __new__(cls, name, charges, min_internal_mass=0,
        max_internal_mass=700, ions=None):

        if ions is None:
            ions = []

        return super(Instrument, cls).__new__(cls, name, charges,
            min_internal_mass, max_internal_mass, ions)


# ION CHANGES
# -----------

WATER_LOSS = DeltaFormulaIon("-H2O", "o", "H-2 O-1", "S,T,E,D")
AMMONIA_LOSS = DeltaFormulaIon("-NH3", "n", "N-1 H-3", "R,K,N,Q")

# ION SERIES
# -----------

# NTERM
# -----
A_ION = SequencingIon("a", 'N', formula='C-1 O-1')
A_ION_H2O_NH3 = A_ION._replace(loss=[WATER_LOSS, AMMONIA_LOSS])

B_ION = SequencingIon("b", 'N')
B_ION_H2O_NH3 = B_ION._replace(loss=[WATER_LOSS, AMMONIA_LOSS])

C_ION = SequencingIon("c", 'N', formula="N H3")

# CTERM
# -----
X_ION = SequencingIon("x", "C", formula="C O H-2")

Y_ION = SequencingIon("y", 'C')
Y_ION_H2O_NH3 = B_ION._replace(loss=[WATER_LOSS, AMMONIA_LOSS])

Z_ION = SequencingIon("z", 'C', formula="N-1 H-2")
Z1_ION = Z_ION._replace(z=1)


# INSTRUMENTS
# -----------

INSTRUMENTS = {
    'ESI-TRAP': Instrument('ESI-TRAP', [1, 2], ions=[
        B_ION_H2O_NH3, Y_ION_H2O_NH3]),
    'ESI-QUAD': Instrument('ESI-QUAD', [1, 2], ions=[
        B_ION_H2O_NH3, Y_ION_H2O_NH3]),
    'ESI-FTICR-CID': Instrument('ESI-FTICR-CID', [1, 2], ions=[
        B_ION_H2O_NH3, Y_ION_H2O_NH3]),
    # TODO: need to define these ions
    'ESI-FTICR-ECD': Instrument('ESI-FTICR-ECD', [1, 2], ions=[
        C_ION, Z_ION, Z1_ION]),

    'MALDI-TOF-TOF': Instrument('MALDI-TOF-TOF', [1], ions=[
        A_ION_H2O_NH3, B_ION_H2O_NH3, Y_ION_H2O_NH3]),
}

CURRENT_INSTRUMENT = 'ESI-TRAP'
