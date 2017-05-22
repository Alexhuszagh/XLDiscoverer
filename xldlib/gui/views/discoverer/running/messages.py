'''
    Gui/Views/Crosslink_Discoverer/Running/messages
    _______________________________________________

    Messages controller for the RunLinkDiscoverer QDialog.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib import exception
from xldlib.controllers import messages
from xldlib.gui.views import widgets
from xldlib.qt import resources as qt
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import decorators, logger


# DATA
# ----

LINKNAME_MESSSAGES = {
    'Standard': 'Standard Links Identified',
    'Low Confidence': 'Low Confidence Links Identified',
    'Fingerprint': 'Mass Fingerprint Links Identified',
    'Incomplete': 'Other Links Identified'
}

LINKTYPE_MESSAGES = {
    'interlink': '    {0} Interlink%(-s)s',
    'intralink': '    {0} Intralink%(-s)s',
    'deadend': '    {0} DeadEnd%(-s)s',
    'multilink': '    {0} MultiLink%(-s)s',
    'single': '    {0} Single%(-s)s',
}


class Label(widgets.Label):
    '''Label with properties for height'''

    # HTML
    # ----
    string = '<font color={0}>{1}<\font>'

    def __init__(self, message, color, bold):
        super(Label, self).__init__(wordWrap=True)

        self.setText(self.string.format(color, message))
        self.setAlignment(qt.ALIGNMENT['HCenter'])
        if bold:
            self.setFont(qt.BOLD_FONT)

    #    PROPERTIES

    @property
    def height(self, adjust=16):
        return self.sizeHint().height() + adjust


# MESSAGES
# --------


@logger.init('gui', 'DEBUG')
class MessageHandler(messages.BaseMessage):
    '''Object to help facilitate messaging events outside of the GUI loop'''

    # QT
    # --
    _qt = qt_config.DIALOGS

    def __init__(self, parent):
        super(MessageHandler, self).__init__(parent)

        self._threads = parent._threads

    #    PROPERTIES

    @property
    def available_height(self):
        return self.desktop_height - self.parent().pos().y() - 50

    @property
    def used_height(self, offset=1):
        '''Estimate for the used height by the QLabels within the layout'''

        count = self.parent().layout.count()
        height = self.parent().last_widget().height
        return self.qt['running'].h + height * count

    #     PUBLIC

    def message(self, message, color, bold=False):
        '''Adds a QLabel-based message to the dialog'''

        label = Label(message, color, bold)
        self.parent().append_widget(label)
        self.adjust_height(label)

    def linkname_message(self, linkname):
        self.message(LINKNAME_MESSSAGES[linkname], "black", True)

    def crosslink_counts(self, linktype, counts):
        message = LINKTYPE_MESSAGES[linktype].format(counts)
        pluralized = exception.convert_number(message, counts)
        self.message(pluralized, "green", False)

    @decorators.overloaded
    def error(self, message):
        '''Displays an error via a QMessageBox and quits active threads'''

        try:
            self._threads.close()
        except Exception:
            # avoids infinite loop
            pass

        if isinstance(message, Exception) or message is Exception:
            text = "Unknown error occured with message {}".format(message.args)
            self.exec_msg(windowTitle="ERROR", text=text)

        else:
            title, text = message
            self.exec_msg(windowTitle=title, text=text)

        self.parent().close()

    #     HELPERS

    def adjust_height(self, widget):
        '''
        Adjusts the parent QDialog dimensions to fit the available
        destkop space or the text size.
        '''

        available = self.available_height
        height = min(self.used_height, available)

        if height != available:
            self.parent().setMinimumSize(self.qt['running'].w, height)

