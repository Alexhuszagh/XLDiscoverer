'''
    Gui/Views/Crosslink_Discoverer/settings/general
    _______________________________________________

    Widget to edit general system settings for Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtCore, QtGui

from xldlib.gui.views.widgets import updating
from xldlib.gui.views import widgets
from xldlib.onstart.main import APP
from xldlib.qt import resources as qt
from xldlib.utils import logger
from xldlib.utils.io_ import qtio

from . import base


# HELPERS
# -------


def process_font(font):
    '''Processes a QFont string to a display font'''

    font = font.split(',')
    # family, size
    return '\t'.join(font[:2])


def getfont(self, model):
    '''Returns a QFont string from a QFontDialog'''

    dialog = FontDialog(model, self)
    dialog.exec_()
    font = dialog.currentFont()
    self.store_from_value(font.toString())

    APP.setFont(font)


# WIDGETS
# -------


@logger.init('gui', 'DEBUG')
class Folder(widgets.Push):
    '''Subclass that resizes to a fixed size with a bound folder icon'''

    def __init__(self, title, widget, parent=None):
        self.title = title
        self.widget = widget

        super(Folder, self).__init__(icon=qt.IMAGES['folder_icon'],
            connect=self.__connect,
            parent=parent)

        self.setStyleSheet("")

    #    PROPERTIES

    @property
    def qt_height(self):
        return self.widget.frameSize().height()

    @property
    def qt_size(self):
        return QtCore.QSize(self.qt_height, self.qt_height)

    #     PUBLIC

    def resize(self):
        self.setFixedSize(self.qt_size)
        self.setIconSize(self.qt_size)

    #     HELPERS

    def __connect(self):
        '''Sets the default path from QFileDialog'''

        path = self.widget.text()
        text = qtio.getopendir(self, self.title, path)
        self.widget.store_from_value(text)


class FontDialog(QtGui.QFontDialog):
    '''Custom QFontDialog which hides effects and system type for defaults'''

    def __init__(self, store, parent):
        super(FontDialog, self).__init__(parent)

        self.__hide()
        font = QtGui.QFont()
        font.fromString(store.data[store.key])

        # BUG: ISSUE is setCurrentFont, doesn't get the styles right, no patch
        self.setCurrentFont(font)

    #     HELPERS

    def __hide(self):
        '''Hides widgets upon startup'''

        for widget in self.children():
            if isinstance(widget, QtGui.QComboBox):
                # QCombobox for writing system
                widget.hide()

            elif isinstance(widget, QtGui.QLabel):
                # QLabel for writing system
                if widget.text() == 'Wr&iting System':
                    widget.hide()

            elif isinstance(widget, QtGui.QGroupBox):
                # contains effects and view
                widget.hide()


# SECTIONS
# --------


@logger.init('gui', 'DEBUG')
class DirectorySection(base.BaseSection):
    '''Section for setting default directories'''

    # SECTION
    # -------
    _title = "Directories"
    _layout = QtGui.QGridLayout

    def __init__(self, parent):
        super(DirectorySection, self).__init__(parent)

        self.input()
        self.output()
        self.add_spacer()

    #    ITEMS

    def input(self):
        '''Sets a paired QPushButton to edit the default input directory'''

        label = widgets.Label("Input: ")
        self.layout.addWidget(label, 1, 0)

        storage = updating.Storage('input_directory')
        inputdir = updating.LineEdit(self, storage,
            tooltip="Default input directory for input files.")
        self.layout.addWidget(inputdir, 1, 1)

        folder = Folder("Get Input Directory", inputdir, self)
        self.layout.addWidget(folder, 1, 2)

    def output(self):
        '''Sets a paired QPushButton to edit the default input directory'''

        label = widgets.Label("Output: ")
        self.layout.addWidget(label, 2, 0)

        storage = updating.Storage('output_directory')
        outputdir = updating.LineEdit(self, storage,
            tooltip="Default output directory for saving files.")
        self.layout.addWidget(outputdir, 2, 1)

        folder = Folder("Get Output Directory", outputdir, self)
        self.layout.addWidget(folder, 2, 2)


@logger.init('gui', 'DEBUG')
class NetworkingSection(base.BaseSection):
    '''Section for network connections'''

    # SECTION
    # -------
    _title = "Networking"

    def __init__(self, parent):
        super(NetworkingSection, self).__init__(parent)

        self.logging()
        self.updates()
        self.add_spacer()

    #    ITEMS

    def logging(self):
        '''Sets whether to send logs by default'''

        storage = updating.Storage('send_logs')
        logs = updating.CheckBox("Send Logs", self, storage,
            tooltip="Send logs to help XL Discoverer updates")

        self.layout.addWidget(logs)

    def updates(self):
        '''Sets whether to send updates by default'''

        storage = updating.Storage('updates_enabled')
        updates = updating.CheckBox("Check Updates", self, storage,
            tooltip="Check for updates upon XL Discoverer start.")

        self.layout.addWidget(updates)


@logger.init('gui', 'DEBUG')
class FontSection(base.BaseSection):
    '''Section for setting XL Discoverer fonts'''

    # SECTION
    # -------
    _title = "Fonts"

    def __init__(self, parent):
        super(FontSection, self).__init__(parent)

        self.system()
        self.add_spacer()

    #    ITEMS

    def system(self):
        '''Sets the default system font'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Default")
        hlayout.addWidget(label)

        storage = updating.Storage('default_font')
        systemfont = updating.ClickButton(self, storage,
            display=process_font,
            connect=getfont,
            tooltip="Set the default font for the application")
        hlayout.addWidget(systemfont)


@logger.init('gui', 'DEBUG')
class IoSection(base.BaseSection):
    '''Section for setting input/output parameters'''

    # SECTION
    # -------
    _title = "Input/Output"

    def __init__(self, parent):
        super(IoSection, self).__init__(parent)

        self.chunksize()
        self.pickling()
        self.add_spacer()

    #    ITEMS

    def chunksize(self):
        '''Sets the default chunksize for I/O events'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Readsize")
        hlayout.addWidget(label)

        storage = updating.Storage('chunk_size')
        chunk = updating.SpinBox(self, storage,
            minimum=0,
            maximum=10000,
            tooltip="Read block size for loading text files.",
            width=75,
            singleStep=1,
            adjust=1024,
            suffix='Kb')
        hlayout.addWidget(chunk)

    def pickling(self):
        '''Sets whether to use pickling for file formats'''

        storage = updating.Storage('enable_pickle')
        pickling = updating.CheckBox("Enable Pickle", self, storage,
            tooltip="Pickling provides file loading improvements, "
            "albeit security risks with data from untrustworthy sources.")

        self.layout.addWidget(pickling)


# PANE
# ----


@logger.init('gui', 'DEBUG')
class GeneralSettings(base.BaseSettings):
    '''Definitions for general settings'''

    def __init__(self, parent):
        super(GeneralSettings, self).__init__(parent)

        self.layout.addWidget(DirectorySection(self))
        self.layout.addWidget(NetworkingSection(self))
        self.layout.addWidget(FontSection(self))
        self.layout.addWidget(IoSection(self))
