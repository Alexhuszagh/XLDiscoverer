'''
    Gui/Views/Crosslink_Discoverer/settings/transitions
    ___________________________________________________

    Widget to edit transition settings for Crosslink Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtCore, QtGui

from xldlib.gui.views import widgets
from xldlib.gui.views.widgets import updating
from xldlib.qt.resources import configurations as qt_config
from xldlib.utils import logger

from . import base


# SECTIONS
# --------


@logger.init('gui', 'DEBUG')
class SearchSection(base.BaseSection):
    '''Section for search parameters during ion chromatogram extraction'''

    # SECTION
    # -------
    _title = "Searching"

    def __init__(self, parent):
        super(SearchSection, self).__init__(parent)

        self.mixed_populations()
        self.global_search()
        self.expand_charges()
        self.charge_range()
        self.add_spacer()

    #    ITEMS

    def mixed_populations(self):
        '''Sets checkbox to include mixed isotope-labeling populations'''

        storage = updating.Storage('include_mixed_populations')
        mixed = updating.CheckBox("Include Mixed Populations", self, storage,
            tooltip="Include crosslinked peptides where each peptide "
            "comes from a different isotope-labeled population.")

        self.layout.addWidget(mixed)

    def global_search(self):
        '''Sets checkbox to include mixed isotope-labeling populations'''

        storage = updating.Storage('quantify_globally')
        globally = updating.CheckBox("Search in all Files", self, storage,
            tooltip="Extract XICs from identified crosslinks in all files.")

        self.layout.addWidget(globally)

    def expand_charges(self):
        '''Sets the checkbox for whether or not to expand the charge range'''

        storage = updating.Storage('expand_charges')
        expand = updating.CheckBox("Expand Charges", self, storage,
            tooltip="Expand the charges included for XIC extraction "
            "to the +/- range")

        self.layout.addWidget(expand)

    def charge_range(self):
        '''Sets the charges to consider above the identified charge'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Charge Range")
        hlayout.addWidget(label)

        storage = updating.Storage('minus_charge_range')
        minus = updating.SpinBox(self, storage,
            minimum=0,
            maximum=5,
            tooltip="Number of charges below the identified charge to "
            "include during XIC extraction.",
            width=50,
            prefix='-')
        hlayout.addWidget(minus)

        storage = updating.Storage('plus_charge_charge')
        plus = updating.SpinBox(self, storage,
            minimum=0,
            maximum=5,
            tooltip="Number of charges above the identified charge to "
            "include during XIC extraction.",
            width=50,
            prefix='+')
        hlayout.addWidget(plus)


@logger.init('gui', 'DEBUG')
class ThresholdSection(base.BaseSection):
    '''Section for setting search hit inclusion'''

    # SECTION
    # -------
    _title = "Thresholds"

    def __init__(self, parent):
        super(ThresholdSection, self).__init__(parent)

        self.xic_fit()
        self.add_spacer()

    #    ITEMS

    def xic_fit(self):
        '''Set the minimum XIC fit score to automatically select an XIC'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("XIC Score Threshold")
        hlayout.addWidget(label)

        storage = updating.Storage('xic_score_threshold')
        xic = updating.DoubleSpinBox(self, storage,
            minimum=0,
            maximum=1,
            tooltip="Minimum weighted score including XIC mass correlation, "
            "peak shape, and size for automatic peak selection.",
            width=75,
            singleStep=0.05)
        hlayout.addWidget(xic)


@logger.init('gui', 'DEBUG')
class FilteringSection(base.BaseSection):
    '''Section for filtering exported transitions'''

    # SECTION
    # -------
    _title = "Filtering"

    def __init__(self, parent):
        super(FilteringSection, self).__init__(parent)

        self.filtering_intensity()
        self.filtering_range()
        self.add_spacer()

        self.filtering_metrics()
        self.filtering_score()
        self.filtering_ev()
        self.add_spacer()

    #    ITEMS

    def filtering_intensity(self):
        '''Sets whether to filter by intensity during export'''

        storage = updating.Storage('filter_transitions_byintensity')
        filter_ = updating.CheckBox("Filter by Intensity", self, storage,
            tooltip="Filter exported XIC ratios by intensity.")

        self.layout.addWidget(filter_)

    def filtering_range(self):
        '''Sets the order of magnitude range for XIC filtering'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Relative Intensity Range")
        hlayout.addWidget(label)

        storage = updating.Storage('intensity_filtering_range')
        range_ = updating.SpinBox(self, storage,
            minimum=1,
            maximum=10,
            preifx="1e",
            tooltip="Relative intensity range (set by finding a minimum\n"
                "threshold relative to the maximum intensity.",
            width=75)
        hlayout.addWidget(range_)

    def filtering_metrics(self):
        '''Sets whether to filter by identification score during export'''

        storage = updating.Storage(
            'filter_transitions_byscore')
        metrics = updating.CheckBox("Filter by Score", self, storage,
            tooltip="Filter exported XIC ratios by identification score.")

        self.layout.addWidget(metrics)

    def filtering_score(self):
        '''Sets the minimum scoring threshold for transition exportation'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Minimum Peptide Score")
        hlayout.addWidget(label)

        storage = updating.Storage('transition_score_threshold')
        score = updating.DoubleSpinBox(self, storage,
            minimum=0.1,
            maximum=100,
            tooltip="Minimum peptide score for quantified "
            "crosslink exportation.",
            width=100)
        hlayout.addWidget(score)

    def filtering_ev(self):
        '''Sets the maximum EV threshold for transition exportation'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Maximum Peptide Score")
        hlayout.addWidget(label)

        storage = updating.Storage('transition_ev_threshold')
        score = updating.ScientificSpinBox(self, storage,
            minimum=1e-10,
            maximum=1.,
            singleStep=0.01,
            tooltip="Maximum peptide EV for quantified "
            "crosslink exportation.",
            width=100)
        hlayout.addWidget(score)


@logger.init('gui', 'DEBUG')
class DocumentSection(base.BaseSection):
    '''Section for transition document settings'''

    # SECTION
    # -------
    _title = "Document"

    def __init__(self, parent):
        super(DocumentSection, self).__init__(parent)

        self.normalization()
        self.sorting()
        self.add_spacer()

    #    ITEMS

    def normalization(self):
        '''Sets the normalization mode for XIC areas and intensities'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Normalize To")
        hlayout.addWidget(label)

        storage = updating.Storage('xic_normalization')
        values = ["Light", "Medium", "Heavy", "Min", "Max"]
        normalization = updating.ComboBox(self, values, storage,
            tooltip="How to normalization XICs areas and intensities "
            "during ratio reporting.",
            width=75)
        hlayout.addWidget(normalization)

    def sorting(self):
        '''Sets the sorting key for transitions document'''

        hlayout = self.add_layout(QtGui.QHBoxLayout)

        label = widgets.Label("Sorting")
        hlayout.addWidget(label)

        storage = updating.Storage('transition_sortkey')
        values = ['RT', 'Peptide', 'Score', 'EV', 'Mod Count']
        sorting = updating.ComboBox(self, values, storage,
            tooltip="Default sorting while constructing the "
            "transitions document.",
            width=75)
        hlayout.addWidget(sorting)


@logger.init('gui', 'DEBUG')
class WindowSection(base.BaseSection):
    '''Section for launching the document editor window during running'''

    # SECTION
    # -------
    _title = "Window"

    def __init__(self, parent):
        super(WindowSection, self).__init__(parent)

        self.launch()
        self.add_spacer()

    #    ITEMS

    def launch(self):
        '''Sets checkbox to include mixed isotope-labeling populations'''

        storage = updating.Storage('launch', qt_config.TRANSITIONS)
        launch = updating.CheckBox("Launch Running Window", self, storage,
            tooltip="Launch the window to validate during\nCrosslink "
            "Discoverer prior to OpenOffice spreadsheet generation.")

        self.layout.addWidget(launch)


@logger.init('gui', 'DEBUG')
class RenderingSection(base.BaseSection):
    '''Section for rendering parameters via the plotting library'''

    # SECTION
    # -------
    _title = "Rendering"

    def __init__(self, parent):
        super(RenderingSection, self).__init__(parent)

        self.opengl()
        self.antialias()
        self.add_spacer()

    #    ITEMS

    def opengl(self):
        '''Sets checkbox to use OpenGL during visualization'''

        storage = updating.Storage('useOpenGL', qt_config.RENDERING)
        opengl = updating.CheckBox("Use OpenGL", self, storage,
            tooltip="Use OpenGL during rendering. Provides performance\n"
            "enhancements, however, is buggy on most systems.")

        self.layout.addWidget(opengl)

    def antialias(self):
        '''Sets checkbox to use antialiasing during visualization'''

        storage = updating.Storage('use_antialiasing')
        antialias = updating.CheckBox("Use Antialising", self, storage,
            tooltip="Use antialiasing during rendering, default True.\n"
            "Not available with OpenGL and some hardware")

        self.layout.addWidget(antialias)


@logger.init('gui', 'DEBUG')
class ExportSection(base.BaseSection):
    '''Section for export settings, including file extensions'''

    # SECTION
    # -------
    _title = "Export"
    _layout = QtGui.QGridLayout

    def __init__(self, parent):
        super(ExportSection, self).__init__(parent)

        self.excel()
        self.document()
        self.image()
        self.add_spacer()

    #    ITEMS

    def excel(self, regex=r"[0-9a-zA-Z]{2,4}"):
        '''Sets the default excel extension for XL Discoverer'''

        label = widgets.Label("OpenOffice")
        self.layout.addWidget(label, 1, 0)

        storage = updating.Storage('excel_extension', qt_config.TRANSITIONS)
        validator = QtGui.QRegExpValidator(QtCore.QRegExp(regex))
        excel = updating.LineEdit(self, storage,
            tooltip="Default extension for OpenOffice spreadsheets.",
            validator=validator,
            width=75,
            attr='extension')
        self.layout.addWidget(excel, 1, 1)

        # stretch factors
        self.add_spacer(args=(1, 2))
        self.layout.setColumnStretch(2, 1)

    def document(self, regex=r"[0-9a-zA-Z]{2,4}"):
        '''Sets the default document extension for XL Discoverer'''

        label = widgets.Label("Document")
        self.layout.addWidget(label, 2, 0)

        storage = updating.Storage('document_extension', qt_config.TRANSITIONS)
        validator = QtGui.QRegExpValidator(QtCore.QRegExp(regex))
        document = updating.LineEdit(self, storage,
            tooltip="Default extension for the transitions docuyment.",
            validator=validator,
            width=75,
            attr='extension')
        self.layout.addWidget(document, 2, 1)

    def image(self, regex=r"[0-9a-zA-Z]{2,4}"):
        '''Sets the default image extension for XL Discoverer'''

        label = widgets.Label("Image")
        self.layout.addWidget(label, 3, 0)

        storage = updating.Storage('image_extension', qt_config.TRANSITIONS)
        validator = QtGui.QRegExpValidator(QtCore.QRegExp(regex))
        image = updating.LineEdit(self, storage,
            tooltip="Default extension for exported images.",
            validator=validator,
            width=75,
            attr='extension')
        self.layout.addWidget(image, 3, 1)

# PANES
# -----


@logger.init('gui', 'DEBUG')
class ExtractionPane(base.BaseSettings):
    '''Definitions for transition extraction settings'''

    def __init__(self, parent):
        super(ExtractionPane, self).__init__(parent)

        self.layout.addWidget(SearchSection(self))
        self.layout.addWidget(ThresholdSection(self))


@logger.init('gui', 'DEBUG')
class ReportingPane(base.BaseSettings):
    '''Definitions for transition filtering settings'''

    def __init__(self, parent):
        super(ReportingPane, self).__init__(parent)

        self.layout.addWidget(FilteringSection(self))
        self.layout.addWidget(DocumentSection(self))


@logger.init('gui', 'DEBUG')
class MiscellaneousPane(base.BaseSettings):
    '''Definitions for miscellaneous transition settings'''

    def __init__(self, parent):
        super(MiscellaneousPane, self).__init__(parent)

        self.layout.addWidget(WindowSection(self))
        self.layout.addWidget(RenderingSection(self))
        self.layout.addWidget(ExportSection(self))


# TABWIDGET
# ---------


@logger.init('gui', 'DEBUG')
class TransitionSettings(QtGui.QTabWidget):
    '''Definitions for transition settings'''

    def __init__(self, parent):
        super(TransitionSettings, self).__init__(parent)

        self.addTab(ExtractionPane(self), "Extraction")
        self.addTab(ReportingPane(self), "Reporting")
        self.addTab(MiscellaneousPane(self), "Miscellaneous")
