'''
    Resources/Qt/Configurations/rendering
    _____________________________________

    Qt rendering definitions for PyQtGraph.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import atexit
import os

import pyqtgraph as pg

from xldlib.general import mapping
from xldlib.resources import paths

__all__ = [
    'RENDERING'
]

# PATHS
# -----

RENDERING_PATH = os.path.join(paths.DIRS['preferences'], 'rendering.json')


# OBJECTS
# -------


class RenderingSettings(mapping.Configurations):
    '''
    Automatically loads and dumps PyQtGraph rendering settings via
    `mapping.Configurations`, however, overrides the `__setitem__`
    method to edit the pg.CONFIG_OPTIONS at the same time.
    '''

    __setter = mapping.Configurations.__setitem__

    def __init__(self, path, defaults):
        super(RenderingSettings, self).__init__(path, defaults)

        for key, value in self.items():
            pg.setConfigOption(key, value)

    def __setitem__(self, key, value):
        '''Set value and edit pg.CONFIG_OPTIONS at same time'''

        self.__setter(key, value)
        pg.setConfigOption(key, value)


# DATA
# ----

RENDERING = RenderingSettings(RENDERING_PATH, [
    ('background', 'w'),
    ('leftButtonPan', False),
    # use the high performance of OpenGL over the introduced bugs by default
    ('useOpenGL', True)
])

# REGISTERS
# ---------

atexit.register(RENDERING.save)
