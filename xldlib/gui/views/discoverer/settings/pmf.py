'''
    Gui/Views/Crosslink_Discoverer/settings/pmf
    ___________________________________________

    Widget to edit Mass Fingerprinting settings for Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.utils import logger

from . import base


# PANES
# -----


@logger.init('gui', 'DEBUG')
class PmfSettings(base.BaseSettings):
    '''Definitions for mass fingerprint settings'''

    def __init__(self, parent):
        super(PmfSettings, self).__init__(parent)

        # TODO: once PMF is implemented
