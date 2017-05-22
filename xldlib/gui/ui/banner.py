'''
    Gui/Ui/banner
    _____________

    Convience methods for inheritance to add a banner to a target widget.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import weakref

from PySide import QtGui

from xldlib.qt.objects import views
from xldlib.qt import resources as qt
from xldlib.utils import decorators


# QLABELS
# -------


class BannerLabel(QtGui.QLabel, views.BaseChildView):
    '''Definitions for a banner label toi add to the UI'''

    def __init__(self, parent, bannerkey):
        super(BannerLabel, self).__init__()

        self.parent = weakref.ref(parent)
        self.bannerkey = bannerkey
        self.setScaledContents(True)
        self.resize()

    #    PROPERTIES

    @property
    def banner(self):
        return qt.IMAGES[self.bannerkey]

    @property
    def width_scalar(self):
        return self.qt['banner'].w

    @property
    def height_scalar(self):
        return self.qt['banner'].h

    @property
    def banner_width(self):
        return int(self.qt_width * self.width_scalar)

    @property
    def banner_height(self):
        return int(self.qt_height * self.height_scalar)

    @property
    def scaled_pixmap(self):
        return self.banner.pixmap(self.banner_width, self.banner_height)

    #     METHODS

    @decorators.overloaded
    def resize(self):
        self.setPixmap(self.scaled_pixmap)
