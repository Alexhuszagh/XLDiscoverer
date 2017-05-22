'''
    Gui/Views/Crosslink_Discoverer/settings/reporterions
    ____________________________________________________

    Widget to edit MS3 quantitation settings for Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.resources import chemical_defs
from xldlib.utils import decorators, logger

from . import base


# WIDGETS
# -------


@logger.init('gui', 'DEBUG')
class CurrentReporterIonBox(updating.ComboBox):
    '''Definitions to select the currently-active reporter ion box'''

    def __init__(self, parent):
        store = updating.Storage('current_reporterions')
        values = sorted(chemical_defs.REPORTER_IONS)
        self.names = {}

        super(CurrentReporterIonBox, self).__init__(parent, values, store)

        self.setToolTip('Current reporter ions used for quantitation')

    #     PUBLIC

    def set_current_text(self, item):
        '''Sets current item based off of item value.'''

        index = self.lookup[item]
        self.setCurrentIndex(index)

    def addItem(self, item):
        '''
        Overrides the native Qt signal to append the item to the value
        list.
        '''

        self.values.append(item)

        name = chemical_defs.REPORTER_IONS[item].name
        self.names[name] = item
        QtGui.QComboBox.addItem(self, name)

    @decorators.overloaded
    def store_value(self):
        self.attribute = self.names[self.currentText()]

    #    SETTERS

    def populate(self, values):
        '''Binds the value list to the current widget + O(1) lookups'''

        for item in values:
            self.addItem(item)


class ErrorSpinBox(updating.DoubleSpinBox):
    '''Definitions for an error-reporting spinbox'''

    def setppm(self):
        self.setMinimum(0)
        self.setMaximum(100)
        self.setSingleStep(1.0)

    def setdalton(self):
        self.setMinimum(0.0)
        self.setMaximum(1.0)
        self.setSingleStep(0.01)


@logger.init('gui', 'DEBUG')
class ErrorComboBox(updating.ComboBox):
    '''Definitions for various error modes'''

    def __init__(self, parent, spinbox):
        storage = updating.Storage('reporterion_error_mode')
        values = ['PPM', 'Da']
        super(ErrorComboBox, self).__init__(parent, values, storage,
            tooltip="Maximum mass error for reporter ion identification.")

        self.spinbox = spinbox

    @decorators.overloaded
    def store_value(self):
        '''Stores the current value and then updates the spinbox'''

        super(ErrorComboBox, self).store_value()

        if self.currentText() == 'PPM':
            self.spinbox.setppm()
        else:
            self.spinbox.setdalton()


# SECTIONS
# --------


@logger.init('gui', 'DEBUG')
class ProductIonSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Reporter Ion Quantitation"

    def __init__(self, parent):
        super(ProductIonSection, self).__init__(parent)

        self.active()
        self.current()
        self.error()
        self.add_spacer()

        self.toggle()

    #    ITEMS

    def active(self):
        '''Sets whether product-level quantitation is set active'''

        storage = updating.Storage('reporterion_quantitation')
        self.quantitation = updating.CheckBox("Reporter Ion Quantitation",
            self, storage,
            tooltip="Use product scans-level reporter ions for quantitation.")
        self.quantitation.clicked.connect(self.toggle)

        self.layout.addWidget(self.quantitation)

    def current(self):
        '''Sets the currently active report ions'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        self.reporterlabel = widgets.Label("Current Reporter Ions")
        hlayout.addWidget(self.reporterlabel)

        self.reporterions = CurrentReporterIonBox(self)
        hlayout.addWidget(self.reporterions)

    def error(self):
        '''Sets the error thresholds for the reporter ion'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Reporter Ion Error")
        hlayout.addWidget(label)

        storage = updating.Storage('reporterion_error')
        self.error = ErrorSpinBox(self, storage,
            tooltip='Maximum error between the experimental and\n'
            'theoreitcal reporter ion mass.',
            width=75)
        hlayout.addWidget(self.error)

        self.reporterionerror = ErrorComboBox(self, self.error)
        hlayout.addWidget(self.reporterionerror)

    #   HELPERS

    def toggle(self):
        '''Toggles the current widget activation'''

        checked = self.quantitation.isChecked()
        self.reporterlabel.setEnabled(checked)
        self.reporterions.setEnabled(checked)
        self.error.setEnabled(checked)
        self.reporterionerror.setEnabled(checked)


# PANES
# -----


@logger.init('gui', 'DEBUG')
class ReporterIonSettings(base.BaseSettings):
    '''Definitions for report ion definitions'''

    def __init__(self, parent):
        super(ReporterIonSettings, self).__init__(parent)

        self.layout.addWidget(ProductIonSection(self))
