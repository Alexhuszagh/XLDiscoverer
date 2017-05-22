'''
    Gui/Views/Widgets/progressbar
    _____________________________

    Standard implementation of the QProgressBar with convenience updating
    and closing methods.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''


# load modules
from PySide import QtGui

from xldlib.qt.objects import views
from xldlib.qt import resources as qt
from xldlib.utils import logger


# PROGRESSBAR
# -----------


@logger.init('gui', 'DEBUG')
class ProgressBar(QtGui.QProgressBar, views.BaseView):
    '''Standard implementation with bar set from 0-100%'''

    def __init__(self, worker, parent=None):
        super(ProgressBar, self).__init__(parent)

        self.setMinimum(0)
        self.setMaximum(100)

        self.set_stylesheet('progressbar')

        worker.part_done.connect(self.updatebar, qt.CONNECTION['Queued'])
        worker.procedure_done.connect(self.close, qt.CONNECTION['Queued'])

        self.show()

    def updatebar(self, value):
        r'''Updates and stylizes bar using %d% format'''

        self.setValue(value)
        perct = "{0}%".format(value)
        self.app.processEvents()
