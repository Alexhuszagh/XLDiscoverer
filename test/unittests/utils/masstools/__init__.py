'''
    Unittests/Utils/Masstools
    _________________________

    Unittests for mass calculations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import charged_mass


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    charged_mass.add_tests(suite)
