'''
    Gui/Views/Crosslink_Discoverer/settings/reports
    _______________________________________________

    Widget to edit selected reports for Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtGui

from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.resources.parameters import column_defs
from xldlib.utils import logger

from . import base


# SECTIONS
# --------


@logger.init('gui', 'DEBUG')
class IncludedSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Included"

    def __init__(self, parent):
        super(IncludedSection, self).__init__(parent)

        self.add_spacer()


@logger.init('gui', 'DEBUG')
class ReportOrderSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Order"

    def __init__(self, parent):
        super(ReportOrderSection, self).__init__(parent)

        self.add_spacer()


@logger.init('gui', 'DEBUG')
class ColumnOrderSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Order"

    def __init__(self, parent):
        super(ColumnOrderSection, self).__init__(parent)

        self.add_spacer()


@logger.init('gui', 'DEBUG')
class ModificationReportingSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Reporting"

    def __init__(self, parent):
        super(ModificationReportingSection, self).__init__(parent)

        self.hierarchical()
        self.concatenate()
        self.isotope_labels()
        self.default_label()
        self.add_spacer()

    #    ITEMS

    def hierarchical(self):
        '''Sets whether to write hierarchical or flattened modifications'''

        storage = updating.Storage('write_hierarchical_modifications')
        hierarchical = updating.CheckBox("Hierarchical", self, storage,
            tooltip="Write Hierarchical (not flattened) modifications.")

        self.layout.addWidget(hierarchical)

    def concatenate(self):
        '''Sets whether to join modifications at the same position'''

        storage = updating.Storage('concatenate_hybrid_modifications')
        concatenate = updating.CheckBox("Concatenate", self, storage,
            tooltip="Join modifications at the same position.")

        self.layout.addWidget(concatenate)

    def isotope_labels(self):
        '''Whether to add isotope labels to the crosslinker'''

        storage = updating.Storage('add_isotopic_labels')
        labels = updating.CheckBox("Crosslinker Isotope Labels",
            self, storage, tooltip="Add isotope labels to the crosslinkers.")

        self.layout.addWidget(labels)

    def default_label(self):
        '''Whether to add isotope labels to the crosslinker'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Default Isotope Label")
        hlayout.addWidget(label)

        storage = updating.Storage('default_isotopic_label')
        default = updating.LineEdit(self, storage,
            tooltip="Default isotope label for the crosslinker (if no "
                "isotope-labeled modifications exist on the peptide).")
        hlayout.addWidget(default)


class ComparativeSection(base.BaseSection):
    '''Class with properties for simplifying accessing comparative data'''

    #  PROPERTIES

    @property
    def comparative(self):
        return self.columns('comparative')

    @property
    def named_comparative(self):
        return self.columns('comparative_named')

    #    PUBLIC

    def key(self, key):
        return column_defs.REPORTNAMES[key]

    def columns(self, key):
        return column_defs.COLUMNS[self.key(key)]


@logger.init('gui', 'DEBUG')
class OtherOrderSection(ComparativeSection):
    '''Section for the order of other of columns in other reports'''

    # SECTION
    # -------
    _title = "Order"

    def __init__(self, parent):
        super(OtherOrderSection, self).__init__(parent)

        self.comparative_order()
        self.named_comparative_order()
        self.add_spacer()

    #    ITEMS

    def comparative_order(self):
        '''Sets the default order for the comparative report'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Comparative")
        hlayout.addWidget(label)

        storage = updating.Storage('order', self.comparative.other)
        values = ['File', 'Crosslinker']
        order = updating.ComboBox(self, values, storage,
            tooltip="Hierarchical header order for the comparative report.")
        hlayout.addWidget(order)

    def named_comparative_order(self):
        '''Sets the default order for the named comparative report'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Named Comparative")
        hlayout.addWidget(label)

        storage = updating.Storage('order', self.named_comparative.other)
        values = ['File', 'Crosslinker']
        order = updating.ComboBox(self, values, storage,
            tooltip="Hierarchical header order for the named "
            "comparative report.")
        hlayout.addWidget(order)


@logger.init('gui', 'DEBUG')
class OtherCountsSection(ComparativeSection):
    '''Section for the counting method in numerical reports'''

    # SECTION
    # -------
    _title = "Counts"

    def __init__(self, parent):
        super(OtherCountsSection, self).__init__(parent)

        self.comparative_counts()
        self.named_comparative_counts()
        self.add_spacer()

    #    ITEMS

    def comparative_counts(self):
        '''Sets the default counts for the comparative report'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Comparative")
        hlayout.addWidget(label)

        storage = updating.Storage('counts', self.comparative.other)
        values = ['Unique', 'Redundant']
        order = updating.ComboBox(self, values, storage,
            tooltip="Counts format for the comparative report.")
        hlayout.addWidget(order)

    def named_comparative_counts(self):
        '''Sets the default counts for the named comparative report'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Named Comparative")
        hlayout.addWidget(label)

        storage = updating.Storage('counts', self.named_comparative.other)
        values = ['Unique', 'Redundant']
        order = updating.ComboBox(self, values, storage,
            tooltip="Counts format for the named comparative report.")
        hlayout.addWidget(order)


@logger.init('gui', 'DEBUG')
class IntegrateSection(base.BaseSection):
    '''Section for intgerating methods in quantitative reports'''

    # SECTION
    # -------
    _title = "Integration"

    def __init__(self, parent):
        super(IntegrateSection, self).__init__(parent)

        self.comparative_integration()
        self.weighted_ratio()
        self.add_spacer()

    #    ITEMS

    def comparative_integration(self):
        '''Sets the default inegration mode for the comparative report'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Comparative")
        hlayout.addWidget(label)

        storage = updating.Storage('ratio_quantitation')
        values = ['Area', 'Intensity']
        order = updating.ComboBox(self, values, storage,
            tooltip="Integration ratios for the quantitative "
            "comparative report.")
        hlayout.addWidget(order)

    def weighted_ratio(self):
        '''Sets whether to use a weighted or unweighted ratio'''

        storage = updating.Storage('weighted_comparative_ratio')
        weighted = updating.CheckBox("Weighted Ratios", self, storage,
            tooltip="Weight quantitative ratios when merging\n"
            "cross-linked peptide linkages.")

        self.layout.addWidget(weighted)


# PANES
# -----


@logger.init('gui', 'DEBUG')
class ReportPane(base.BaseSettings):
    '''Pane for report selection editing'''

    def __init__(self, parent):
        super(ReportPane, self).__init__(parent)

        self.layout.addWidget(IncludedSection(self))
        self.layout.addWidget(ReportOrderSection(self))


@logger.init('gui', 'DEBUG')
class ColumnPane(base.BaseSettings):
    '''Pane for column order editing'''

    def __init__(self, parent):
        super(ColumnPane, self).__init__(parent)

        self.layout.addWidget(ColumnOrderSection(self))


@logger.init('gui', 'DEBUG')
class ModificationPane(base.BaseSettings):
    '''Pane for modification reporting settings'''

    def __init__(self, parent):
        super(ModificationPane, self).__init__(parent)

        self.layout.addWidget(ModificationReportingSection(self))


@logger.init('gui', 'DEBUG')
class OtherPane(base.BaseSettings):
    '''How to order the comparative header'''

    def __init__(self, parent):
        super(OtherPane, self).__init__(parent)

        self.layout.addWidget(OtherOrderSection(self))
        self.layout.addWidget(OtherCountsSection(self))
        self.layout.addWidget(IntegrateSection(self))


# TABWIDGET
# ---------


@logger.init('gui', 'DEBUG')
class SpreadsheetSettings(QtGui.QTabWidget):
    '''Definitions for spreadsheet settings'''

    def __init__(self, parent):
        super(SpreadsheetSettings, self).__init__(parent)

        self.addTab(ReportPane(self), "Reports")
        self.addTab(ColumnPane(self), "Columns")
        self.addTab(ModificationPane(self), "Modifications")
        self.addTab(OtherPane(self), "Miscellanious")
