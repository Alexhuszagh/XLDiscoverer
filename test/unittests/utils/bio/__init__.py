'''
    Unittests/Utils/Bio
    ___________________

    Test suite for biological file-format parsers.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from . import fasta, uniprot_xml


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    fasta.add_tests(suite)
    uniprot_xml.add_tests(suite)
