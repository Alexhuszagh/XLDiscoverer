


# load modules
import os
import sys
import unittest

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../../..'))
sys.path.append(path)

import configs2
from libs.gene_database import sequence
from libs.utils import io_
from objects import protein


class TestSequence(unittest.TestCase):

    def setUp(self):

        self.protein = protein.Protein('MVKVGVNGFGRIGRLVTRAAFNSGKVDVVAINDPFIDL'
            'HYMVYMFQYDSTHGKFHGTVKAENGKLVINGKAITIFQERDPANIKWGDAGAEYVVESTGVFTTM'
            'EKAGAHLKGGAKRVIISAPSADAPMFVMGVNHEKYDNSLKIVSNASCTTNCLAPLAKVIHDHFGI'
            'VEGLMTTVHAITATQKTVDGPSGKLWRDGRGAAQNIIPASTGAAKAVGKVIPELNGKLTGMAFRV'
            'PTPNVSVVDLTCRLEKAAKYDDIKKVVKQASEGPLKGILGYTEDQVVSCDFNSATHSSTFDAGAG'
            'LNDHFVKLISWYDNEFGYSNRVVDLMVHMASKE', name='GAPDH',
            uniprot_id='P46406')
        self.table = sequence.ProteinTable()

    def test_io(self):

        self.table.new()
        self.table.close()
        self.table.open(configs2.TEMP_GENE)

        # test saving
        outpath = os.path.join(io_.TMP_DIR, 'testing')
        self.table.save(outpath)
        self.assertEqual(os.path.exists(outpath), True)
        io_.remove_file(outpath)

        self.table.close()

    def test_adding(self):
        '''Tests adding genes to the database'''

        self.table.new([self.protein])
        self.assertEqual(self.table.sequences.shape, (1,))
        self.assertSequenceEqual(self.table.sequences.read(),
            [self.protein.sequence])

        self.assertEqual(self.table.names.shape, (1,))
        self.assertSequenceEqual(self.table.names.read(),
            [self.protein.name])

        self.table.genes.flush()
        uniprot_id, length, mw = self.table.genes[0]

        self.assertEqual(uniprot_id, self.protein.uniprot_id)
        self.assertEqual(length, self.protein._length)
        self.assertEqual(mw, self.protein.mw)

        self.table.close()


if __name__ == '__main__':
    unittest.main()
