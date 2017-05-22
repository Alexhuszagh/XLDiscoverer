'''
    Vendors/Thermo_Finnigan
    _______________________

    Tools to parse the Thermo Finnigan vendor file formats. Makes extensive
    use of the COM interface and ctypes.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

from .api import ThermoFinniganApi

__all__ = [
    'api', 'c_compound_types',
    'compound_types', 'lib_def'
]
