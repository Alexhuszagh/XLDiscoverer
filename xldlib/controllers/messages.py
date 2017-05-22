'''
    Controllers/messages
    ____________________

    Inheritable object for launching warning QMessageBoxes.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import operator as op
from functools import wraps

from PySide import QtGui

from xldlib.qt.objects import views
from xldlib.utils import logger


# ERRORS
# ------


def warningbox(error, btn_names=None):
    '''Execs a QtGui.QMessageBox upon excepting an error'''

    def decorator(f):
        @wraps(f)
        def newf(self, *args, **kwds):
            try:
                return f(self, *args, **kwds)

            except error as msg:
                msg, title = msg.args[0]

                logger.Logging.warning(msg)
                rep = self.exec_msg(btn_names, text=msg, windowTitle=title)
                if rep == QtGui.QMessageBox.No or rep == QtGui.QMessageBox.Ok:
                    return False
                else:
                    return True

        return newf
    return decorator


# MESSAGES
# --------


class BaseMessage(views.BaseView):
    '''Base attributes for various dialog settings to simplify launching'''

    #     FUNCTIONS

    def exec_msg(self, buttonnames=None, **kwds):
        '''Execs a QtGui.QMessageBox from the given widget'''

        kwds.setdefault('parent', self.app.splashwindow)

        if buttonnames is not None:
            generator = (getattr(QtGui.QMessageBox, i) for i in buttonnames)
            kwds.update(standardButtons=op.or_(*generator))

        popup = QtGui.QMessageBox(**kwds)
        return popup.exec_()
