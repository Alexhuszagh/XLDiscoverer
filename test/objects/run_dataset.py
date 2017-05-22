
# load modules
import os
import sys
import unittest

path = os.path.realpath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(path)

import configs2
from libs.utils import io_
from objects import run_dataset


class TestRunData(unittest.TestCase):
    '''
    Ensures equal data adding and high-speed data addition with minimal
    performance issues for the matched data
    '''

    def setUp(self):
        '''Create mob object and bind'''

        self.dataset = run_dataset.RunDataset()

    def test_io_(self):

        self.dataset.new()
        self.dataset.close()
        self.dataset.open(configs2.TEMP_RUN)

        # test saving
        outpath = os.path.join(io_.TMP_DIR, 'testing')
        self.dataset.save(outpath)
        self.assertEqual(os.path.exists(outpath), True)
        io_.remove_file(outpath)

        self.dataset.close()

    def test_adding_matched(self):

        self.dataset.open(configs2.TEMP_RUN)
        self.dataset.set_rawmode()
        self.dataset.add_rows(5)
        table = self.dataset.get_file_row(0)

        # check the defaults
        row = table.row
        row['peptide'] = 'LKEEYQSLIR'
        row['mods'] = [0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0] + [0] * 40
        row['formula'] = 'O18 N15 C57 H95'
        row['num'] = 2198
        row['start'] = 32
        # row['rank'] = 0
        row['id'] = 'Q9Y3C8'
        row['mz'] = 682.849
        row['score'] = 25.5
        row['ev'] = 0.0012
        row['ppm'] = 2.1
        row['z'] = 2

        row['precursor_mz'] = 618.06410000000005
        row['precursor_z'] = 4
        row['precursor_rt'] = 20.760000000000002
        row['precursor_num'] = 2196

        row.append()
        table.flush()

        self.assertEqual(table.cols.rank[0], 1)

if __name__ == '__main__':
    unittest.main()
