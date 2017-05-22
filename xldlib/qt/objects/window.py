'''
    Qt/Objects/window
    _________________

    Base class definitions shared by all windowed objects.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtCore

from xldlib.qt import resources as qt

from .views import BaseView


__all__ = [
    'WindowObject',
]


# QOBJECT
# -------


class WindowObject(BaseView):
    '''Base class definition for windowed objects (QMainWindow, QDialog)'''

    # WINDOW STATE
    # ------------
    size_changed = QtCore.Signal(int, int)
    position_changed = QtCore.Signal(int, int)
    windowstate_changed = QtCore.Signal(object)

    #     EVENTS

    def ignore_resize_event(self, event):
        '''
        Ignore calls to self.resizeEvent

        Args:
            event (QResizeEvent): window resize event data
        '''

        event.ignore()

    def track_resize_event(self, event):
        '''
        Track and store new window dimensions.

        Args:
            event (QResizeEvent): window resize event data
        '''

        event.accept()
        rect = self.rect()
        self.qt_window.w = rect.width()
        self.qt_window.h = rect.height()

        self.size_changed.emit(rect.width(), rect.height())
        self.qt.edited.emit(self.windowkey)

    def track_move_event(self, event):
        '''
        Track and store new window position.

        Args:
            event (QMoveEvent): window move event data
        '''

        event.accept()
        pos = self.pos()
        self.qt_window.x = pos.x()
        self.qt_window.y = pos.y()

        self.position_changed.emit(pos.x(), pos.y())
        self.qt.edited.emit(self.windowkey)

    def track_change_event(self, event):
        '''
        Track QWindowStateChangeEvents to return the window size and
        position to normal after undoing a WindowMaximized event.

        Args:
            event (QWindowStateChangeEvent): window state event data
        '''

        if event.type() == QtCore.QEvent.WindowStateChange:
            if self.windowState() & qt.WINDOW['Maximized']:
                # if is maximized
                event.accept()

            elif event.oldState() & qt.WINDOW['Maximized']:
                # if was maximized
                event.accept()
                self.resize_nostate()

    #    CONFIGURATIONS

    def set_rect_qt(self):
        '''Set window rect from the `self.qt` data'''

        self.resize_qt()
        self.move_qt()
        self.set_windowstate_qt()

    def resize_qt(self):
        '''Resize window from `self.qt` data'''

        self.resize(self.qt_window.w, self.qt_window.h)

    def move_qt(self):
        '''Move window from `self.qt` data'''

        self.move(self.qt_window.x, self.qt_window.y)

    def set_windowstate_qt(self):
        '''Set window state from `self.qt` data'''

        default = self.qt.get('window_state', 'WindowNoState')
        window_state = getattr(QtCore.Qt, default, QtCore.Qt.WindowNoState)
        self.setWindowState(window_state)

    def set_fixed_size_qt(self):
        '''Set fixed window size from `self.qt` data'''

        self.setFixedSize(self.qt_window.w, self.qt_window.h)

    def set_icon_qt(self):
        '''Set window icon from `self.qt` data'''

        self.setWindowIcon(qt.IMAGES[self.qt['icon']])

    def set_title_qt(self):
        '''Set window title from `self.qt` data'''

        self.setWindowTitle(self.qt['title'])

    def set_stylesheet_qt(self):
        '''Set window styles from `self.qt` data'''

        self.setStyleSheet(self.qt['stylesheet'])

    #   OTHER METHODS

    def resize_nostate(self):
        '''Resize window to restore geometry after undoing Maximized state'''

        rect = self.rect()
        pos = self.pos()

        # take the minimal of the current framesize and the available
        available_width = self.desktop_width - pos.x()
        width = min(available_width, rect.width())

        available_height = self.desktop_height - pos.y()
        height = min(available_height, rect.height())

        self.resize(width, height)

    def track_window(self):
        '''Track window data and write to `self.qt`'''

        self.resizeEvent = self.track_resize_event
        self.moveEvent = self.track_move_event
        self.changeEvent = self.track_change_event

    def set_top_window(self):
        '''Set window modal and on top with a title bar'''

        self.setModal(True)
        self.set_windowflags('Window|StaysOnTopHint')

    def set_window_noframe(self):
        '''Remove title bar from window'''

        self.set_windowflags('Window|FramelessHint')

    def set_window_nobuttons(self):
        '''Set window modal with title bar but no window buttons'''

        self.setModal(True)
        self.set_windowflags('Window|TitleHint|StaysOnTopHint')

    def set_windowflags(self, flag):
        '''
        Set the QtCore.Qt.WindowFlags for the window object

        Args:
            flag (str, QtCore.Qt.WindowType): window flag to describe window
        '''

        self.setWindowFlags(self.__windowflagchecker(flag))

    #    NON-PUBLIC

    def __windowflagchecker(self, flag):
        '''Normalize QtCore.Qt.WindowType types'''

        return qt.WINDOW_FLAG.normalize(flag)
