'''
    Unittests/Utils/Bio/uniprot_xml
    _______________________________

    Test suite for the UniProt KB XML parser.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os
import unittest

from xldlib.resources import paths
from xldlib.utils.bio import uniprot_xml

from ._data import SEQUENCE

# ITEMS
# -----

UNIPROT_XML = {
    'mnemonic': 'ALBU_BOVIN',
    'name': 'Serum albumin',
    'id': 'P02769',
    'sequence': SEQUENCE
}


# CASES
# -----


class ParseTest(unittest.TestCase):
    '''Test parsing compressed and non-compressed XML files'''

    def setUp(self):
        '''Set up unittests'''

        home = paths.DIRS['home']
        self.path = os.path.join(home, 'test', 'files')

    def test_parse(self):
        '''Test XML parsing for each file'''

        files = [
            os.path.join(self.path, 'bio', 'file.xml'),
            os.path.join(self.path, 'bio', 'file.xml.gz'),
            os.path.join(self.path, 'bio', 'file.xml.bz2')
        ]
        for path in files:
            with uniprot_xml.Parse(path) as parser:
                item = next(iter(parser))
                self.assertEquals(item, UNIPROT_XML)

    def tearDown(self):
        '''Tear down unittests'''

        del self.path


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ParseTest('test_parse'))
