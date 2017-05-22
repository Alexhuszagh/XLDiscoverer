'''
    Gui/Views/Crosslink_Discoverer/Running/dialog
    _____________________________________________

    QDialog upon the initiation and running of Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from collections import namedtuple, OrderedDict
from functools import reduce

from PySide import QtGui

from xldlib import exception
from xldlib.gui.ui import layouts
from xldlib.gui.views import widgets
from xldlib.gui.views.dialogs.base import KeyBindingDialog
from xldlib.onstart import args
from xldlib.qt.objects import threads
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger
from xldlib.xlpy import run

from .io_ import IoHandler
from .messages import MessageHandler
from .threads import ThreadHandler


# CONSTANTS
# ---------

SCROLL_LAYOUT = QtGui.QGridLayout

# OBJECTS
# -------

Button = namedtuple("Button", "icon attrname")


# SETTINGS
# --------

BINDINGS = [
    ('message', ['_messages', 'message']),
    ('error', ['_messages', 'error']),
    ('procedure_done', ['set_summary']),
    ('finished', ['_threads', 'fin']),
    ('paused', ['_threads', 'pause'])
]

SAVE_BUTTONS = OrderedDict([
    ('session', Button('save_session_icon', 'session')),
    ('excel', Button('save_openoffice_icon', 'excel')),
    ('transitions', Button('save_transitions_icon', 'transitions')),
    ('fingerprint', Button('save_fingerprinting_icon', 'fingerprint')),
])


# RUNNING
# -------


@logger.init('gui', 'DEBUG')
class RunDiscoverer(KeyBindingDialog):
    '''
    QWidget with GridLayout with embedded QProgressBar.
    Initializes worker and background threads to run Xl Discoverer,
    while displaying progress.
    '''

    # QT
    # --
    _qt = qt_config.DIALOGS
    _windowkey = 'running'

    def __init__(self, parent, quantitative=False):
        super(RunDiscoverer, self).__init__(parent)

        self.quantitative = quantitative

        layouts.set_scroll(self, SCROLL_LAYOUT)
        self.set_window_data()
        self.set_threads()

        self._threads = ThreadHandler(self)
        self._io = IoHandler(self)
        self._messages = MessageHandler(self)

        self.bind_worker_signals()
        self.set_keybindings()

        # TODO: RunningEvents, other events

    #    PROPERTIES

    @property
    def worker(self):
        return self.threads[0]

    @property
    def background(self):
        return self.self.threads[1]

    #  EVENT HANDLING

    @logger.call('gui', 'debug')
    def showEvent(self, event):
        '''Initializes the target threads upon showing the dialog'''

        progress = widgets.ProgressBar(self.worker, self)
        self.layout.addWidget(progress, 0, 0)
        self.app.setOverrideCursor(qt.CURSOR['Wait'])
        event.accept()

        for thread in self.threads:
            thread.start()

        self.app.discovererwindow.isrunning = True

    @logger.call('gui', 'debug')
    def closeEvent(self, event):
        '''Initializes the target threads upon showing the dialog'''

        if self._threads.check_close_event(event):
            self._threads.close()
            self._threads.reset_cursor()

    def focusInEvent(self, event):
        '''Overrides the main event to ensure the cursor is a wait'''

        event.accept()
        if self._threads._paused:
            self._threads.reset_cursor()

    #  PUBLIC FUNCTIONS

    def add_widget(self, widget, row, column=0, rowspan=1, columnspan=4):
        self.layout.addWidget(widget, row, column, rowspan, columnspan)

    def append_widget(self, widget):
        rows = self.layout.count()
        self.add_widget(widget, rows)

    def last_widget(self):
        return self.layout.itemAt(self.layout.count() - 1).widget()

    #     SETTERS

    def set_window_data(self):
        '''Sets the window data for the dialog'''

        self.setWindowTitle("Progress...")

        self.set_top_window()
        self.resize_qt()
        self.move_qt()

        policy = (QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Preferred)
        self.setSizePolicy(*policy)

    def set_keybindings(self):
        '''Stores the window keybindings depending on the entered mode'''

        self.bind_close()
        if args.DEBUG:
            self.bind_pdb()

        if args.TRACE:
            self.bind_trace()

    def set_threads(self):
        '''Sets the running threads for XL Discoverer'''

        self.threads = []
        worker = run.CrosslinkDiscovererThread(self, self.quantitative)
        self.threads.append(worker)

        background = threads.BackgroundThread(worker, self)
        self.threads.append(background)

    def set_summary(self):
        '''Generates the results summary with the crosslink counts'''

        self._threads.reset_cursor()
        self.clear()

        self._messages.message("Xl Discoverer Summary", "black", True)
        self.set_crosslink_report()
        self.set_skipped_files()
        self.set_save_buttons()

    def set_crosslink_report(self):
        '''Sets the crosslink count total for the widget'''

        counts = self.worker.helper.counts
        for linkname in counts:
            self._messages.linkname_message(linkname)
            for linktype, frozen in counts[linkname].items():
                count = len(frozen)
                self._messages.crosslink_counts(linktype, count)

    def set_skipped_files(self):
        '''Sets the ignore file warnings for the XL Discoverer run'''

        offset = self.worker.files.offset
        if offset:
            message = "{0} File%(-s)s not Analyzed".format(offset)
            pluralized = exception.convert_number(message, offset)
            self._messages.message(pluralized, "red", True)

    def set_save_buttons(self):
        '''Adds save buttons for the Excel spreadsheet'''

        rowcount = self.layout.rowCount()
        self.add_widget(widgets.Divider(self), rowcount)

        for index, key in enumerate(('session', 'excel')):
            widget = self.get_save_button(key)
            self.add_widget(widget, rowcount+1, 2*index, columnspan=2)

        # add the data-dependent save buttons
        matched = self.worker.matched
        keys = ()
        if matched.quantitative and matched.fingerprinting:
            keys = ('transitions', 'fingerprint')
        elif matched.quantitative:
            keys = ('transitions',)
        elif matched.fingerprinting:
            keys = ('fingerprint',)

        for index, key in enumerate(keys):
            column = 2 * index + (len(keys) % 2)
            btn = self.get_save_button(key)
            self.add_widget(btn, rowcount+2, column, columnspan=2)

    #     GETTERS

    def get_save_button(self, key):
        '''Returns the SaveButton from the key'''

        button = SAVE_BUTTONS[key]
        icon = qt.IMAGES[button.icon]
        fun = getattr(self._io, button.attrname)
        return widgets.Save(icon=icon, connect=fun, parent=self)

    #     BINDINGS

    def bind_worker_signals(self):
        '''Binds the worker signals to slots'''

        for worker_attrname, attrname in BINDINGS:
            worker_attr = getattr(self.worker, worker_attrname)
            attr = reduce(getattr, attrname, self)

            worker_attr.connect(attr, qt.CONNECTION['Queued'])

    #     HELPERS

    def clear(self):
        '''Clears the current layout'''

        # clear the holder widget, remake and reset the scroll layout
        self.layout.deleteLater()
        self.widget.deleteLater()

        self.widget = widgets.Widget()
        self.layout = SCROLL_LAYOUT(self.widget)
        self.scrollarea.setWidget(self.widget)

        # reset the widget size
        self.setMinimumSize(0, 0)
        self.resize_qt()
