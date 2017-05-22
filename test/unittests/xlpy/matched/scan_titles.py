'''
    Unittests/XlPy/Matched/scan_titles
    __________________________________

    Tests for matching scan filters and extract scan information.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.xlpy.matched import scan_titles


# ITEMS
# -----

FILTERS = [
    'file_00.1632.1632.2.dta',
    'TITLE=Scan 2193 (rt=20.738) [file_00.raw]',
    'Scan 1227 (rt=18.332) [file_00.raw]'
]


# CASES
# -----


class ScanTitleTest(unittest.TestCase):
    '''Test regexes properly match and extract scan title information'''

    #     TESTS

    def test_filters(self):
        '''Run tests on every scan filter within `FILTERS`'''

        for title in FILTERS:
            self._test_filter(title)

    #    NON-PUBLIC

    def _test_filter(self, title):
        '''Test regex matching and data extraction from a `title` string'''

        parser = scan_titles.TitleFormatter()
        match = parser(title)
        self.assertTrue(match.group('frac'))
        self.assertTrue(match.group('num').isdigit())


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ScanTitleTest('test_filters'))
