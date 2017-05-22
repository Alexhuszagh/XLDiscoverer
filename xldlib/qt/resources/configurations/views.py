'''
    Qt/Resources/Configurations/views
    _________________________________

    Qt view definitions for window and widget data.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules/submodules
import atexit
import os

from namedlist import namedlist

from xldlib.general import mapping
from xldlib.utils import signals
from xldlib.qt.resources import scaling
from xldlib.resources import extensions, paths

__all__ = [
    'CONTEXTS',
    'CROSSLINK_DISCOVERER',
    'DIALOGS',
    'FINGERPRINT',
    'SPLASH',
    'TABLES',
    'TRANSITIONS',
]


# PATHS
# -----

VIEWS = paths.DIRS['views']

SPLASH_PATH = os.path.join(VIEWS, 'splash.json')
CROSSLINK_DISCOVERER_PATH = os.path.join(VIEWS, 'discoverer.json')
TRANSITION_PATH = os.path.join(VIEWS, 'transitions.json')
FINGERPRINT_PATH = os.path.join(VIEWS, 'fingerprint.json')
DIALOGS_PATH = os.path.join(VIEWS, 'dialogs.json')
CONTEXTS_PATH = os.path.join(VIEWS, 'contexts.json')


# OBJECTS
# -------

Dimensions = namedlist("Dimensions", "w h")
Frame = namedlist("Frame", "x y w h")
XlDiscovererMode = namedlist("XlDiscovererMode", "icon title banner")
Thresholds = namedlist("Thresholds", "upper lower")


class ViewConfigurations(mapping.Configurations):
    '''Definitions which defines a view_edited signal back to edit'''

    def __init__(self, *args, **kwds):
        super(ViewConfigurations, self).__init__(*args, **kwds)

        self.edited = signals.Signal()
        self.edited.connect(self.modified)

    #     PUBLIC

    def modified(self, key):
        '''
        Include modified value for data serialization.

        Args:
            key (str): dictionary key
        '''

        self.changed[key] = self[key]

# DATA
# ----

SPLASH = ViewConfigurations(SPLASH_PATH, [
    ('app', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y,
        w=max(6*scaling.INCREMENT, 480),
        h=8*scaling.INCREMENT)),
    ('title', 'XL Discoverer'),
    ('window_state', 'WindowNoState'),
    ('stylesheet', "background-color: white"),
    ('menubutton_size', 0.35),
    ('banner', Dimensions(w=0.8, h=0.3)),
    ('icon', 'splash_icon')
])

CROSSLINK_DISCOVERER = ViewConfigurations(
    CROSSLINK_DISCOVERER_PATH, [
        ('app', Frame(x=scaling.QUARTER_X,
            y=scaling.TOP_Y,
            w=max(6*scaling.INCREMENT, 480),
            h=8*scaling.INCREMENT)),
        ('stylesheet', "background-color: white"),
        ('window_state', 'WindowNoState'),
        ('banner', Dimensions(w=0.8, h=0.3)),
        ('menubutton_size', 0.35),
        ('default', XlDiscovererMode("xldiscoverer_icon",
            "CrossLink Discoverer", "xldiscoverer_banner")),
        ('quantitative', XlDiscovererMode("quantitative_xldiscoverer_icon",
            "Quantitative CrossLink Discoverer",
            "quantitative_xldiscoverer_banner")),
        ('crosslinker_view', 'crosslinkers'),
        ('crosslinkerbutton_size', Dimensions(w=0.35, h=0.05)),
        # EXTENSIONS
        # ----------
        ('session_extension', extensions.SESSION),
        ('excel_extension', extensions.SPREADSHEET),
        ('transitions_extension', extensions.TRANSITIONS),
        ('fingerprint_extension', extensions.FINGERPRINT),
    ],
)

TRANSITIONS = ViewConfigurations(TRANSITION_PATH, [
    ('app', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y,
        w=max(6*scaling.INCREMENT, 480),
        h=8*scaling.INCREMENT)),
    ('stylesheet', "background-color: white"),
    ('title', 'Transitions Viewer'),
    ('header', ['Crosslinked Peptide XICs']),
    ('window_state', 'WindowNoState'),
    ('icon', 'transition_icon'),
    ('path', paths.FILES['transition']),
    ('launch', True),
    # EXTENSIONS
    # ----------
    ('excel_extension', extensions.SPREADSHEET),
    ('document_extension', extensions.TRANSITIONS),
    ('image_extension', extensions.PNG),
    # QSTANDARDITEM ICONS
    # -------------------
    ('dotp_thresholds', Thresholds(0.85, 0.5)),
    ('gaussian_thresholds', Thresholds(0.7, 0.3))]
)

FINGERPRINT = ViewConfigurations(FINGERPRINT_PATH, [
    ('app', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y,
        w=max(6*scaling.INCREMENT, 480),
        h=8*scaling.INCREMENT)),
    ('stylesheet', "background-color: white"),
    ('title', 'Peptide Mass Fingerprint Viewer'),
    ('header', ['Mass Fingerprint Peptides']),
    ('window_state', 'WindowNoState'),
    ('icon', 'fingerprint_icon'),
    ('path', paths.FILES['fingerprint']),
    ('launch', True),
    # EXTENSIONS
    # ----------
    ('excel_extension', extensions.SPREADSHEET),
    ('document_extension', extensions.FINGERPRINT),
    ('image_extension', extensions.PNG)]
)

DIALOGS = ViewConfigurations(DIALOGS_PATH, [
    ('about', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        # Ensure text fits, but scale to size
        w=max(150, 2*scaling.INCREMENT),
        h=50+0.5*scaling.INCREMENT)),
    ('license', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        # Ensure text fits, but scale to size
        w=max(400, 5*scaling.INCREMENT),
        h=3*scaling.INCREMENT)),
    ('io', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        w=2*scaling.INCREMENT,
        h=0.5*scaling.INCREMENT)),
    ('settings', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        w=250+2.5*scaling.INCREMENT,
        h=300+3*scaling.INCREMENT)),
    ('running', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        w=3*scaling.INCREMENT,
        h=0.6*scaling.INCREMENT)),
    ('find', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        w=4*scaling.INCREMENT,
        h=2*scaling.INCREMENT)),
    ('findall', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        w=4*scaling.INCREMENT,
        h=2*scaling.INCREMENT)),
    ('uniprot', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        w=5*scaling.INCREMENT,
        h=2*scaling.INCREMENT)),
    ('running_close', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        w=4*scaling.INCREMENT,
        h=scaling.INCREMENT))
])

CONTEXTS = ViewConfigurations(CONTEXTS_PATH, [
    ('transitions', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        # Ensure text fits, but scale to size
        w=6*scaling.INCREMENT,
        h=5*scaling.INCREMENT)),
    ('table', Frame(x=scaling.QUARTER_X,
        y=scaling.TOP_Y + 1.5*scaling.INCREMENT,
        # Ensure text fits, but scale to size
        w=4*scaling.INCREMENT,
        h=5*scaling.INCREMENT)),
    ('title', 'Keyboard Shortcuts'),
])

TABLES = {
    'row_height': 0.5*scaling.INCREMENT
}

# REGISTERS
# ---------

atexit.register(SPLASH.save)
atexit.register(CROSSLINK_DISCOVERER.save)
atexit.register(TRANSITIONS.save)
atexit.register(FINGERPRINT.save)
atexit.register(DIALOGS.save)
