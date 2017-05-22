'''
    Unittests/Qt/Resources/Configurations/rendering
    _______________________________________________

    Test suite for Qt rendering configurations.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

import pyqtgraph as pg

from xldlib.qt.resources import configurations as qt_config


# CASES
# -----


class ConfigTest(unittest.TestCase):
    '''Tests for editing pyqtgraph settings along with user elements'''

    def test_config(self):
        '''Test PyQtGraph configurations edited with RENDERING'''

        state = qt_config.RENDERING['useOpenGL']
        self.assertEquals(state, pg.getConfigOption('useOpenGL'))

        qt_config.RENDERING['useOpenGL'] = not state
        self.assertEquals(not state, pg.getConfigOption('useOpenGL'))

        qt_config.RENDERING['useOpenGL'] = state

# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ConfigTest('test_config'))
