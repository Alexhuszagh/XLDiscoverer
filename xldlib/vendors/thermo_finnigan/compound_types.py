'''
    Vendors/Thermo_Finnigan/compound_types
    ______________________________________

    Defines compound data types, such as namedtuples, for
    facile scan extraction.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load objects/functions
from collections import namedtuple

# Compound Types

ScanHeaderInfo = namedtuple("ScanHeaderInfo",
    "num_packets start_time "
    "low_mass high_mass total_ion_count "
    "base_peak_mass base_peak_intensity "
    "num_channels uniform_time frequency")

PrecursorRange = namedtuple("PrecursorRange",
    "ms_order first_precursor_mass "
    "last_precursor_mass valid")

MassList = namedtuple("MassList",
    "peak_width mass_list "
    "peak_flags size")

SegmentedMassList = namedtuple("SegmentedMassList",
    "peak_width mass_list "
    "peak_flags size segments "
    "segment_count mass_range")

MassRange = namedtuple("MassRange", "low high")

MSOrderData = namedtuple("MSOrderData",
    "mass isolation_width collision_energy "
    "first_mass last_mass width_offset")
