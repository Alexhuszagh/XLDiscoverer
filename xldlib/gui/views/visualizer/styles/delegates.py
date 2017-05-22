'''
    Gui/Views/Visualizer/Trees/delegates
    ____________________________________

    StandardItemModel delegate to alter spacing and add HTML styles
    to the model in QTreeViews.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
from PySide import QtCore, QtGui

from xldlib.qt import resources as qt


# DELEGATE
# --------


class StandardItemDelegate(QtGui.QStyledItemDelegate):
    '''Custom implementation of a styled standard item delegate'''

    # SCALING
    # -------
    adjust = 0.85

    #     PROPERTIES

    def paint(self, painter, option, index):
        '''Paint the standard item'''

        self.set_flags(option, painter)
        options = QtGui.QStyleOptionViewItemV4(option)

        self.initStyleOption(options, index)
        painter.save()

        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)

        # get focus rect and selection background
        options.text = ""
        if options.widget:
            style = options.widget.style()
        else:
            style = QtGui.QApplication.style()
        style.drawControl(QtGui.QStyle.CE_ItemViewItem, options, painter)

        # draw using our rich text document
        widthoffset = self._get_offset(options, index, style)
        painter.translate(options.rect.left() + widthoffset,
            options.rect.top())
        rect = QtCore.QRectF(0, 0, options.rect.width(), options.rect.height())
        doc.drawContents(painter, rect)

        painter.restore()

    def editorEvent(self, event, model, option, index):
        '''Custom editor event for hover events'''

        cls = super(StandardItemDelegate, self)
        return cls.editorEvent(event, model, option, index)

    def sizeHint(self, option, index):
        '''Returns a size hint for the defined text'''

        # initialize new options
        options = QtGui.QStyleOptionViewItemV4(option)
        self.initStyleOption(options, index)

        # create the size
        doc = QtGui.QTextDocument()
        doc.setHtml(options.text)
        doc.setTextWidth(options.rect.width())
        size = QtCore.QSize(doc.idealWidth(), self.adjust*doc.size().height())

        return size

    #      SETTERS

    def set_flags(self, option, painter):
        '''Sets the flag options for various item states'''

        if option.state & QtGui.QStyle.State_Selected:
            self.set_selected(painter)

            if option.state & QtGui.QStyle.State_Active:
                self.set_active(option, painter)
            else:
                self.set_inactive(option, painter)

        elif option.state & QtGui.QStyle.State_MouseOver:
            self.set_hover(option, painter)

        else:
            self.set_default(painter)

    def set_selected(self, painter):
        '''Sets a selected palette for the painter'''

        painter.setPen(QtGui.QPen('#567dbc', width=1))

    def set_active(self, option, painter):
        '''Sets an active palette for the painter'''

        gradient = self.getgradient(option, '#6ea1f1', '#567dbc')
        painter.fillRect(option.rect, QtGui.QBrush(gradient))

    def set_inactive(self, option, painter):
        '''Sets an inactive palette for the painter'''

        gradient = self.getgradient(option, '#6b9be8', '#577fbf')
        painter.fillRect(option.rect, QtGui.QBrush(gradient))

    def set_hover(self, option, painter):
        '''Sets a hover palette for the painter'''

        gradient = self.getgradient(option, '#e7effd', '#cbdaf1')
        painter.fillRect(option.rect, QtGui.QBrush(gradient))
        painter.setPen(QtGui.QPen('#bfcde4', width=1))

    def set_default(self, painter):
        '''Sets the default widget border'''

        painter.setPen(QtGui.QPen('#d9d9d9', width=1))

    #      GETTERS

    def getgradient(self, option, color1, color2):
        '''Returns a QLinearGradient with the embedded colors'''

        gradient = QtGui.QLinearGradient(option.rect.topLeft(),
            option.rect.topRight())

        gradient.setColorAt(0, color1)
        gradient.setColorAt(1, color2)

        return gradient

    def _get_offset(self, options, index, style):
        '''Returns the width offset of the given item'''

        # add decoration shift
        widthoffset = []

        # add checkbox changes
        item = index.model().itemFromIndex(index)
        if item.isCheckable():
            rect = self._get_checkbox_rect(style)
            widthoffset.append(rect.width() + 5)

        # add icon changes
        icon_size = item.icon().availableSizes()
        dec_size = options.decorationSize
        if icon_size:
            adjust = dec_size.height() / icon_size[0].height()
            widthoffset.append(icon_size[0].width() * adjust + 5)

        return sum(widthoffset)

    @staticmethod
    def _get_checkbox_rect(style):
        '''Gets the checkbox rect'''

        option = QtGui.QStyleOptionButton()
        checkbox = QtGui.QStyle.SE_CheckBoxIndicator
        return style.subElementRect(checkbox, option, None)
