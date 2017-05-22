'''
    Unittests/Gui/check_imports
    ___________________________

    Unittests to ensure invalid imports are caught upon initialization.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.onstart import check_imports


# ITEMS
# -----

STANDARD = (
    check_imports.Module('Os', 'os',
        condition=lambda x: True,
        message='This module should be found'),
)

MISSING = (
    check_imports.Module('MissingModule', 'missing_module',
        condition=lambda x: True,
        message='This module should be missing'),
)


# OBJECTS
# -------


class Module(object):
    '''Fake module object with a `__version__`'''

    __version__ = '1.3.1'


# CASES
# -----


class ImportTest(unittest.TestCase):
    '''Test missing imports'''

    def test_version(self):
        '''Test module versions are correctly checked on import'''

        self.assertTrue(check_imports.check_version((1, 3, 0), Module()))
        self.assertFalse(check_imports.check_version((1, 3, 2), Module()))

    def test_imports(self):
        '''Test missing imports can be resolved upon initialization'''

        standard = list(check_imports.yield_missing(STANDARD))
        self.assertEquals(standard, [])

        missing = list(check_imports.yield_missing(MISSING))
        self.assertEquals(missing, list(MISSING))


# TESTS
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ImportTest('test_version'))
    suite.addTest(ImportTest('test_imports'))
