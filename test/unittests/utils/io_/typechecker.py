'''
    Unittests/Utils/Io_/typechecker
    _______________________________

    Tests for file-type checker functions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import os
import unittest

from xldlib.resources import paths
from xldlib.utils.io_ import typechecker


# CASES
# -----


class FileFormatTest(unittest.TestCase):
    '''Test file-format matching'''

    def setUp(self):
        '''Set up unittests'''

        home = paths.DIRS['home']
        self.path = os.path.join(home, 'test', 'files')

    def test_seek_start(self):
        '''Test seek_start decorator keeps file position'''

        with open(os.path.join(self.path, 'FullMS Quant', 'c.txt')) as f:
            self.assertEquals(f.tell(), 0)

            for length in (20, 40, 200):
                with typechecker.seek_start(f) as newf:
                    newf.read(length)
                    self.assertTrue(length -1 <= f.tell() <= length + 1)
                self.assertEquals(f.tell(), 0)

    def test_raw(self):
        '''Test Thermo Finnigan Raw file matching'''

        with open(os.path.join(self.path, 'Thermo.raw'), 'rb') as f:
            self.assertTrue(typechecker.raw(f))

    def test_hdf5(self):
        '''Test HDF5 file matching'''

        path = os.path.join(self.path, 'HDF.h5')
        self.assertTrue(typechecker.hdf5(path))

    def test_sqlite(self):
        '''Test SQLite3 file matching'''

        with open(os.path.join(self.path, 'SQLite3.db'), 'rb') as f:
            self.assertTrue(typechecker.sqlite(f))

    def test_gz(self):
        '''Test gzip file matching'''

        path = os.path.join(self.path, 'compressed', 'file.gz')
        with open(path, 'rb') as f:
            self.assertTrue(typechecker.gz(f))

    def test_bz2(self):
        '''Test bzip2 file matching'''

        path = os.path.join(self.path, 'compressed', 'file.bz2')
        with open(path, 'rb') as f:
            self.assertTrue(typechecker.bzip2(f))

    def test_zip(self):
        '''Test PK zipfile file matching'''

        path = os.path.join(self.path, 'compressed', 'file.zip')
        self.assertTrue(typechecker.pkzip(path))

    def test_tar(self):
        '''Test bzip2 file matching'''

        paths = [
            os.path.join(self.path, 'compressed', 'file.tar'),
            os.path.join(self.path, 'compressed', 'file.tar.gz'),
            os.path.join(self.path, 'compressed', 'file.tar.bz2')
        ]
        for path in paths:
            self.assertTrue(typechecker.tar(path))

    def test_xml(self):
        '''Test Extensible Markup Language file matching'''

        paths = [
            os.path.join(self.path, 'PP pepXML', 'MS3.pep.xml'),
            os.path.join(self.path, 'mzML', 'scans.mzML'),
            os.path.join(self.path, 'mzXML', 'scans.mzXML')
        ]
        for path in paths:
            with open(path, 'rb') as f:
                self.assertTrue(typechecker.xml(f))

    def test_mime(self):
        '''Test Multipurpose Internet Mail Extensions file matching'''

        with open(os.path.join(self.path, 'Mascot.dat')) as f:
            self.assertTrue(typechecker.mime(f))

    def tearDown(self):
        '''Tear down unittests'''

        del self.path


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(FileFormatTest('test_seek_start'))
    suite.addTest(FileFormatTest('test_raw'))
    suite.addTest(FileFormatTest('test_hdf5'))
    suite.addTest(FileFormatTest('test_sqlite'))
    suite.addTest(FileFormatTest('test_gz'))
    suite.addTest(FileFormatTest('test_bz2'))
    suite.addTest(FileFormatTest('test_zip'))
    suite.addTest(FileFormatTest('test_tar'))
    suite.addTest(FileFormatTest('test_xml'))
    suite.addTest(FileFormatTest('test_mime'))
