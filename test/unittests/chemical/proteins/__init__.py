'''
    Unittests/Chemical/Proteins
    ___________________________

    Unit tests for protein object definitions and resources.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import (configurations, enzyme, peptide,
               peptide_list, protein, sequence_tools)


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    configurations.add_tests(suite)
    enzyme.add_tests(suite)
    peptide.add_tests(suite)
    peptide_list.add_tests(suite)
    protein.add_tests(suite)
    sequence_tools.add_tests(suite)
