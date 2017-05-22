'''
    Gui/Views/Crosslink_Discoverer/crosslinkers
    ___________________________________________

    View to select, edit, and add new crosslinkers.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from PySide import QtCore, QtGui

from xldlib.controllers import bindings
from xldlib.definitions import partial
from xldlib.gui.views import widgets
from xldlib.qt.resources import configurations as qt_config
from xldlib.resources import chemical_defs
from xldlib.utils import decorators, logger

from . import profiles


# DATA
# ----

WIDGETS = [
    ('Crosslinkers', 'crosslinkers'),
    ('Isotope Labeling', 'isotope_labeling')
]


# QPUSHBUTTON
# -----------


@logger.init('gui', 'DEBUG')
class CrossLinkerButton(widgets.GradientButton):
    '''Custom implementation with a large size hint and colored border'''

    def __init__(self, crosslinker, parent):
        super(CrossLinkerButton, self).__init__(crosslinker.name, parent)

        self.crosslinker = crosslinker

        self.setCheckable(True)
        self.setChecked(crosslinker.active)

        self.clicked.connect(self.store_value)
        self.resize()

    #    PROPERTIES

    @property
    def adjust(self):
        return self.parent().qt['crosslinkerbutton_size']

    @property
    def width(self):
        return self.parent().qt['app'].w * self.adjust.w

    @property
    def height(self):
        return self.parent().qt['app'].h * self.adjust.h

    @property
    def active(self):
        return self.crosslinker.active

    @active.setter
    def active(self, value):
        self.crosslinker.active = value
        self.setChecked(value)
        chemical_defs.CROSSLINKER_EDITED_SIGNAL.emit(self.crosslinker)

    #     PUBLIC

    def store_value(self):
        self.active = self.isChecked()

    def resize(self):
        self.setFixedSize(self.width, self.height)


# TOGGLER
# -------


@logger.init('gui', 'DEBUG')
class ToggleView(widgets.Widget):
    '''
    Adds a layout to toggle the current view (from selecting crosslinkers
    to selecting profile entries.
    '''

    # QT
    # --
    _qt = qt_config.CROSSLINK_DISCOVERER

    def __init__(self, parent):
        super(ToggleView, self).__init__(parent)

        self.set_layout(QtGui.QVBoxLayout)

        self.set_togglebar()
        self.toggle_checkstate()
        self.layout.addWidget(widgets.Divider(self))

    #    PROPERTIES

    @property
    def view(self):
        return self.qt['crosslinker_view']

    @view.setter
    def view(self, value):
        self.qt['crosslinker_view'] = value

    @property
    def crosslinker(self):
        return self.view == 'crosslinkers'

    #     SETTERS

    def set_togglebar(self):
        '''Adds paired QPushbuttons to toggle the current display'''

        layout = QtGui.QHBoxLayout()
        self.layout.addLayout(layout)

        for title, attrname in WIDGETS:
            slot = partial(self.clicked, attrname)
            button = widgets.ClickButton(title, slot, checkable=True)

            layout.addWidget(button)
            setattr(self, attrname, button)

    #     HELPERS

    def clicked(self, key):
        '''
        Changes the current hierarchical/level_separated checksattes
        and the input_files backing store.
        '''

        self.view = key
        self.toggle_checkstate()
        self.parent().change_view()

    def toggle_checkstate(self):
        '''
        Toggles the current checkstates for the level_separated/hierarchical
        input mods
        '''

        self.crosslinkers.setChecked(self.crosslinker)
        self.isotope_labeling.setChecked(not self.crosslinker)


# SELECTION VIEWS
# ---------------


@logger.init('gui', 'DEBUG')
class SelectCrosslinkersView(widgets.Widget, bindings.Keys):
    '''Widget view to select crosslinkers'''

    # QT
    # --
    _qt = qt_config.CROSSLINK_DISCOVERER

    def __init__(self, parent):
        super(SelectCrosslinkersView, self).__init__(parent)

        self.set_layout(QtGui.QVBoxLayout)
        self.set_size_policy('Expanding', 'Expanding')
        self.set_crosslinkers()

        self.app.discovererwindow.size_changed.connect(self.changesize)

    #     SETTERS

    def set_crosslinkers(self, interval=2):
        '''Adds the crosslinkers to the current layout'''

        self.crosslinkers = []
        for id_, crosslinker in chemical_defs.CROSSLINKERS.items():
            button = CrossLinkerButton(crosslinker, self)
            self.crosslinkers.append(button)

            # add to layout, starts with 1-index for id_
            if id_ % interval:
                layout = QtGui.QHBoxLayout()
                self.layout.addLayout(layout)

            layout.addWidget(button)

    #     HELPERS

    def save(self):
        chemical_defs.CROSSLINKERS.save()

    @decorators.overloaded
    def changesize(self):
        '''Changes the crosslinker widget sizes upon window size changes'''

        for crosslinker in self.crosslinkers:
            crosslinker.resize()


@logger.init('gui', 'DEBUG')
class SelectIsotopeLabelsView(widgets.Widget):
    '''Widget view to select isotope label profiles'''

    def __init__(self, parent):
        super(SelectIsotopeLabelsView, self).__init__(parent)

        self.set_layout(QtGui.QVBoxLayout)
        self.view = profiles.ProfileSelectionView(self)
        self.layout.addWidget(self.view)

    #    PROPERTIES

    @property
    def index(self):
        return self.view.index

    @property
    def profile(self):
        return self.view.profile

    @property
    def table(self):
        return self.view.table

    #  EVENT HANDLING

    def closeEvent(self, event):
        '''On editing of the QcomboBox::lineEdit()'''

        self.profile.removenulls()
        event.accept()

    #     HELPERS

    def save(self):
        '''Saves the current profile'''

        self.profile.removenulls()
        if self.index not in chemical_defs.PROFILES:
            chemical_defs.PROFILES[self.index] = self.profile
            self.view.profile_combo.appendnew()

        self.table.reset_view()
        chemical_defs.PROFILES.save()


VIEWS = {
    'crosslinkers': SelectCrosslinkersView,
    'isotope_labeling': SelectIsotopeLabelsView
}


# MAIN VIEW
# ---------


@logger.init('gui', 'DEBUG')
class CrosslinkerView(widgets.Widget):
    '''
    QWidget with embedded cross-linkers for facile selection, as
    well as configurable addition/deletion of crosslinker widgets.
    '''

    # QT
    # --
    _qt = qt_config.CROSSLINK_DISCOVERER
    closed = QtCore.Signal(object)

    def __init__(self, parent, quantitative):
        super(CrosslinkerView, self).__init__(parent)

        self.quantitative = quantitative

        self.set_layout(QtGui.QVBoxLayout)
        self.set_header()

        if quantitative:
            self.add_spacer()
            self.toggler = ToggleView(self)
            self.layout.addWidget(self.toggler)

        self.add_spacer()
        self.set_view()

        if isinstance(self.view, SelectCrosslinkersView):
            self.set_editbar()
            self.set_divider()
        self.set_savebar()

    #    PROPERTIES

    @property
    def crosslinker(self):
        return self.qt['crosslinker_view'] == 'crosslinkers'

    #     SETTERS

    def set_header(self):
        '''Adds a header to the layout'''

        self.header = widgets.Banner('Crosslinker & Labeling Settings')
        self.layout.addWidget(self.header)

    def set_view(self):
        '''Sets the selection view'''

        if self.quantitative:
            cls = VIEWS[self.qt['crosslinker_view']]
            self.view = cls(self)
            self.layout.insertWidget(4, self.view)

        else:
            self.view = SelectCrosslinkersView(self)
            self.layout.insertWidget(2, self.view)

    def set_editbar(self):
        '''Adds a bar to edit/delete crosslinkers'''

        self.edit_bar = widgets.Widget()
        layout = QtGui.QHBoxLayout()
        self.edit_bar.setLayout(layout)
        self.layout.addWidget(self.edit_bar)

        edit = widgets.StandardButton("Add/Edit Crosslinker")
        layout.addWidget(edit)

        delete = widgets.StandardButton("Delete Crosslinker")
        layout.addWidget(delete)

    def set_divider(self):
        '''Adds a distinct divider to the layout'''

        self.divider = widgets.SunkenDivider(self)
        self.layout.addWidget(self.divider)

    def set_savebar(self):
        '''Adds a return/save bar to the layout'''

        layout = QtGui.QHBoxLayout()
        self.layout.addLayout(layout)

        done_editing = widgets.ClickButton("Done Editing", self.close)
        layout.addWidget(done_editing)

        save = widgets.ClickButton("Save", self.save)
        layout.addWidget(save)

    #     HELPERS

    def change_view(self):
        '''Changes the view after changing the view switch'''

        self.view.hide()
        self.layout.removeWidget(self.view)
        self.view.deleteLater()
        del self.view

        if hasattr(self, "edit_bar"):
            for attrname in ('edit_bar', 'divider'):
                attr = getattr(self, attrname)
                if self.crosslinker:
                    attr.show()
                else:
                    attr.hide()

        self.set_view()

    def save(self):
        self.view.save()

    #  EVENT HANDLING

    def closeEvent(self, event):
        '''Shows the parent menu widget upon a close event'''

        self.view.close()
        self.closed.emit(self)
        event.accept()
