

# load modules
import os
import sys
import unittest

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(path)

import configs2

from objects import enzyme
from objects import protein

class TestTrypsin(unittest.TestCase):
    '''
    Tests a Trypsin protease
    '''

    def setUp(self):
        '''Create mob object and bind'''

        protease = configs2.ENZYMES['Trypsin']
        self.trypsin = enzyme.ProteolyticEnzyme(protease)

        self.protein = protein.Protein('MVKVGVNGFGRIGRLVTRAAFNSGKVDVVAINDPFIDL'
            'HYMVYMFQYDSTHGKFHGTVKAENGKLVINGKAITIFQERDPANIKWGDAGAEYVVESTGVFTTM'
            'EKAGAHLKGGAKRVIISAPSADAPMFVMGVNHEKYDNSLKIVSNASCTTNCLAPLAKVIHDHFGI'
            'VEGLMTTVHAITATQKTVDGPSGKLWRDGRGAAQNIIPASTGAAKAVGKVIPELNGKLTGMAFRV'
            'PTPNVSVVDLTCRLEKAAKYDDIKKVVKQASEGPLKGILGYTEDQVVSCDFNSATHSSTFDAGAG'
            'LNDHFVKLISWYDNEFGYSNRVVDLMVHMASKE', name='GAPDH',
            uniprot_id='P46406')

    def test_cuts(self):

        self.protein.peptides.cut_sequence(self.trypsin)
        print([i.sequence for i in self.protein.peptides])
        self.assertEqual(self.protein.peptides[0].sequence, 'MVK')

        self.assertEqual(self.protein.peptides[-1].sequence, 'E')
        self.assertEqual(self.protein.peptides[-20].sequence,
            'IVSNASCTTNCLAPLAK')

if __name__ == '__main__':
    unittest.main()
