'''
    Onstart/app
    ___________

    Custom QApplication definition and methods.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import weakref

from PySide import QtGui


# APPLICATION
# -----------


class App(QtGui.QApplication):
    '''
    QApplication subclass with properties and memos to facilitate
    finding top-level widgets, active QThreads, and temporary files
    marked for removal on application exit. These are provided
    through the class variables `views`, `threads`, and `temporary_files`.
    '''

    # MEMOS
    # -----
    views = {}
    threads = weakref.WeakValueDictionary()
    temporary_files = set()

    def __init__(self, *args, **kwds):
        process = kwds.pop('process', False)
        super(App, self).__init__(*args, **kwds)

        if not process:
            self._setup_font()

    #    PROPERTIES

    @property
    def splashwindow(self):
        return self._top_level('SplashWindow')

    @property
    def discovererwindow(self):
        return self._top_level("DiscovererWindow")

    @property
    def fingerprintwindow(self):
        return self._top_level('FingerprintWindow')

    @property
    def transitionwindow(self):
        return self._top_level('TransitionWindow')

    @property
    def discovererthread(self):
        return self.threads['CrosslinkDiscovererThread']

    @property
    def backgroundthread(self):
        return self.threads['BackgroundThread']

    #     SETUP

    def _setup_font(self):
        '''Set default application font'''

        from xldlib.resources.parameters import defaults

        font = QtGui.QFont()
        font.fromString(defaults.DEFAULTS['default_font'])
        self.setFont(font)

    #    NON-PUBLIC

    def _top_level(self, key):
        '''Find top level widget from class name identifier'''

        try:
            return self.views[key]
        except KeyError:
            # need to set the proper memo
            toplevel = [i for i in self.topLevelWidgets() if key in repr(i)][0]
            self.views[key] = toplevel
            return toplevel
