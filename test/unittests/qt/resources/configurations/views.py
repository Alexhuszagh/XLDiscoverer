'''
    Unittests/Qt/Resources/Configurations/views
    ___________________________________________

    Test signal-slot mechanism for configuration editing.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import unittest

from xldlib.qt.resources import configurations as qt_config

# CASES
# -----


class ConfigTest(unittest.TestCase):
    '''Test bound signals connected to setters'''

    def test_config(self):
        '''Test `conf.edited` is connected to `conf.changed`'''

        if 'menubutton_size' not in qt_config.SPLASH.changed:
            qt_config.SPLASH.edited.emit('menubutton_size')
            self.assertIn('menubutton_size', qt_config.SPLASH.changed)
            del qt_config.SPLASH.changed['menubutton_size']

        else:
            del qt_config.SPLASH.changed['menubutton_size']
            qt_config.SPLASH.edited.emit('menubutton_size')
            self.assertIn('menubutton_size', qt_config.SPLASH.changed)


# SUITE
# -----


def add_tests(suite):
    '''Add tests to the unittest suite'''

    suite.addTest(ConfigTest('test_config'))
