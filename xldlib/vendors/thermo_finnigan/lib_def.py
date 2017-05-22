'''
    Vendors/Thermo_Finnigan/lib_def
    _______________________________

    Contains library definitions for the MSFileReader API.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import tables as tb

# LIBRARY DEFINITIONS
# -------------------

Sample_Type = tb.Enum([
    'Unknown',
    'Blank',
    'QC',
    'Standard Clear (None)',
    'Standard Update (None)',
    'Standard Bracket (Open)',
    'Standard Bracket Start (multiple brackets)',
    'Standard Bracket End (multiple brackets'
])

Controller_Type = tb.Enum({
    'No device': -1,
    'MS': 0,
    'Analog': 1 ,
    'A/D card': 2 ,
    'PDA': 3 ,
    'UV': 4
})

Cutoff_Type = tb.Enum([
    'None (all values returned)',
    'Absolute (in intensity units)',
    'Relative (to base peak)'
])

Chromatogram_Type = {}

Chromatogram_Operator = tb.Enum([
    'None (single chro only)',
    'Minus (subtract chro 2 from chro 1)',
    'Plus (add chro 1 and chro 2)'
])

Smoothing_Type = tb.Enum([
    'None (no smoothing)',
    'Boxcar',
    'Gaussian'
])

Activation_Type = tb.Enum([
    'CID',
    'MPD',
    'ECD',
    'PQD',
    'ETD',
    'HCD',
    'Any activation type',
    'SA',
    'PTR',
    'NETD',
    'NPTR'
])

Mass_Analyser_Type = tb.Enum([
    'ITMS',
    'TQMS',
    'SQMS',
    'TOFMS',
    'FTMS',
    'Sector'
])

Collision_Type = tb.Enum([
    'CID',
    'PQD',
    'ETD',
    'HCD'
])

Scan_Type = tb.Enum([
    'ScanTypeFull',
    'ScanTypeSIM',
    'ScanTypeZoom',
    'ScanTypeSRM'
])

Scan_Order = tb.Enum({
    'Neutral gain': -3,
    'Neutral loss': -2,
    'Parent scan': -1,
    'Any scan order': 0,
    'MS': 1,
    'MS2': 2,
    'MS3': 3,
    'MS4': 4,
    'MS5': 5,
    'MS6': 6,
    'MS7': 7,
    'MS8': 8,
    'MS9': 9,
    'MS10': 10
})

Multiplex_Type = tb.Enum([
    'Off',
    'On',
    'Accept any Multiplex'
])
