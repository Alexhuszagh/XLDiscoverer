'''
    Unittests/Utils/Bio/fasta
    _________________________

    Test suite for the UniProt KB FASTA parser.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os
import unittest

from xldlib.resources import paths
from xldlib.utils.bio import fasta

from ._data import SEQUENCE

# ITEMS
# -----

UNIPROT_FASTA = {
    'description': 'Serum albumin OS=Bos taurus GN=ALB PE=1 SV=4\n',
    'sp': ('P02769', 'ALBU_BOVIN'),
    'sequence': SEQUENCE
}


# CASES
# -----


class ParseTest(unittest.TestCase):
    '''Test parsing compressed and non-compressed FASTA files'''

    def setUp(self):
        '''Set up unittests'''

        home = paths.DIRS['home']
        self.path = os.path.join(home, 'test', 'files')

    def test_parse(self):
        '''Test FASTA parsing for each file'''

        files = [
            os.path.join(self.path, 'bio', 'file.fasta'),
            os.path.join(self.path, 'bio', 'file.fasta.gz'),
            os.path.join(self.path, 'bio', 'file.fasta.bz2')
        ]
        for path in files:
            with fasta.Parse(path) as parser:
                item = next(iter(parser))
                self.assertEquals(item, UNIPROT_FASTA)

    def tearDown(self):
        '''Tear down unittests'''

        del self.path


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ParseTest('test_parse'))
