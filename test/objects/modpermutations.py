

# load modules
import os
import sys
import unittest

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(path)

from objects import modpermutations
from objects import protein

class TestModObject(unittest.TestCase):
    '''
    Tests the mod objects to be correct.
    '''

    def setUp(self):
        '''Create mob object and bind'''

        self.protein = protein.Protein('MVKVGVNGFGRIGRLVTRAAFNSGKVDVVAINDPFIDL'
            'HYMVYMFQYDSTHGKFHGTVKAENGKLVINGKAITIFQERDPANIKWGDAGAEYVVESTGVFTTM'
            'EKAGAHLKGGAKRVIISAPSADAPMFVMGVNHEKYDNSLKIVSNASCTTNCLAPLAKVIHDHFGI'
            'VEGLMTTVHAITATQKTVDGPSGKLWRDGRGAAQNIIPASTGAAKAVGKVIPELNGKLTGMAFRV'
            'PTPNVSVVDLTCRLEKAAKYDDIKKVVKQASEGPLKGILGYTEDQVVSCDFNSATHSSTFDAGAG'
            'LNDHFVKLISWYDNEFGYSNRVVDLMVHMASKE', name='GAPDH',
            uniprot_id='P46406')
        self.protein.peptides.cut_sequence()
        self.protein.peptides.concatenate()
        self.peptide = self.protein.peptides[-1]

        self.mod_perms = modpermutations.ModPermutations()

    def test_mob_permutations(self):

        permutations = self.mod_perms(self.peptide, self.protein._length)

        names, formula = next(permutations)
        self.assertSequenceEqual(names, ['XL:A-Sulfenic'])
        self.assertEqual(int(formula.mass()), 1518)

        names, formula = next(permutations)
        self.assertSequenceEqual(names, ['Oxidation', 'XL:A-Sulfenic'])
        self.assertEqual(int(formula.mass()), 1534)

if __name__ == '__main__':
    unittest.main()
