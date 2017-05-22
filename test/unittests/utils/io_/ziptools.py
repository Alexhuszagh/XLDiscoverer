'''
    Unittests/Utils/Io_/typechecker
    _______________________________

    Tests for file decompression methods.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os
import unittest

from xldlib.resources import paths
from xldlib.utils.io_ import ziptools


# CONSTANTS
# ---------

HEADER = b'File contents\n'


# CASES
# -----


class DecompressionTest(unittest.TestCase):
    '''Tests for file decompresssion'''

    def setUp(self):
        '''Set up unittests'''

        home = paths.DIRS['home']
        self.path = os.path.join(home, 'test', 'files')

    def test_gz(self):
        '''Test gzip file matching'''

        path = os.path.join(self.path, 'compressed', 'file.gz')
        with open(path, 'rb') as f:
            fileobj = ziptools.decompress(f)
            self.assertEquals(fileobj.read(), HEADER)

    def test_bz2(self):
        '''Test bzip2 file matching'''

        path = os.path.join(self.path, 'compressed', 'file.bz2')
        with open(path, 'rb') as f:
            fileobj = ziptools.decompress(f)
            self.assertEquals(fileobj.read(), HEADER)

    def test_zip(self):
        '''Test PK zipfile file matching'''

        path = os.path.join(self.path, 'compressed', 'file.zip')
        with ziptools.decompress(path) as fileobj:
            self.assertEquals(fileobj.read(), HEADER)

    def test_tar(self):
        '''Test bzip2 file matching'''

        files = [
            os.path.join(self.path, 'compressed', 'file.tar'),
            os.path.join(self.path, 'compressed', 'file.tar.gz'),
            os.path.join(self.path, 'compressed', 'file.tar.bz2')
        ]
        for path in files:
            with ziptools.decompress(path) as fileobj:
                self.assertEquals(fileobj.read(), HEADER)

    def tearDown(self):
        '''Tear down unittests'''

        del self.path


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(DecompressionTest('test_gz'))
    suite.addTest(DecompressionTest('test_bz2'))
    suite.addTest(DecompressionTest('test_zip'))
    suite.addTest(DecompressionTest('test_tar'))
