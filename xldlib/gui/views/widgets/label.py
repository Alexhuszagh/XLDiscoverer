'''
    Gui/Views/Widgets/label
    _______________________

    Subclasses for QLabels to inherit from a common object.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtGui

from xldlib.qt.objects import views


# LABELS
# ------


class Label(QtGui.QLabel, views.BaseView):
    '''Inherits from the base Qt class and the common object'''


class Banner(Label):
    '''Large, bolded, underlined label as a banner over a view'''

    def __init__(self, text):
        super(Banner, self).__init__(text)

        self.set_stylesheet('banner')
