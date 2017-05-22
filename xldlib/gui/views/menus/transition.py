'''
    Gui/Views/Menus/fingerprint
    ___________________________

    Sets the menu for a Peptide Mass Fingerprint visualizer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from . import base

from xldlib.gui.views.discoverer import settings

# load objects/functions
from collections import OrderedDict

from xldlib.definitions import partial


# OBJECTS
# -------


class TransitionMenu(base.BaseMenu):
    '''Adds a transition menu to the TransitionWindow'''

    #      SETTERS

    def set_menus(self):
        '''Adds all the child menus to the list'''

        menus = OrderedDict()
        menus['&File'] = self.file
        menus['&Edit'] = self.edit
        menus['&View'] = self.view
        menus['&Graph'] = self.graph
        menus['&Export'] = self.export
        menus['Help'] = self.help

        for name, fun in menus.items():
            menu = self.parent.menuBar().addMenu(name)
            fun(menu)

    #       MENUS

    def file(self, menu):
        '''Adds all the file entries to the widgets'''

        items = OrderedDict()
        items['&Open'] = OrderedDict()
        items['&Open']['&File'] = {
            'shortcut': 'Ctrl+O',
            'statusTip': 'Open Transitions',
            'triggered': self.io.open
        }
        items['&Open']['&Add'] = {
            'shortcut': 'Ctrl+Shift+A',
            'statusTip': 'Add Transitions',
            'triggered': partial(self.io.open, mode='add')
        }

        items['&Save'] = {
            'shortcut': 'Ctrl+S',
            'statusTip': 'Save Transitions',
            'triggered': self.io.save
        }
        items['&Save As'] = {
            'shortcut': 'Ctrl+Shift+S',
            'statusTip': 'Save Transitions As',
            'triggered': self.io.saveas
        }
        items['&Save File(s)'] = {
            'statusTip': 'Save Transition File(s)',
            'triggered': self.io.save_files
        }
        items['&Save Image'] = {
            'shortcut': 'Ctrl+I',
            'statusTip': 'Save Current Image',
            'triggered': self.io.save_image
        }

        items[len(items)] = None

        items['&Close'] = OrderedDict()
        items['&Close']['&All'] = {
            'statusTip': 'Close All File(s)',
            'shortcut': 'Ctrl+C',
            'triggered': self.io.close_files
        }
        items['&Close']['&File(s)'] = {
            'statusTip': 'Close Selected File(s)',
            'shortcut': 'Ctrl+Shift+C',
            'triggered': self.io.close_selected_files
        }

        items[len(items)] = None

        items['&Exit'] = {
            'shortcut': 'Ctrl+Q',
            'statusTip': 'Exit Window',
            'triggered': self.parent.close
        }

        self.set_items(menu, items)

    def edit(self, menu):
        '''Adds all the edit entries to the widgets'''

        items = OrderedDict()
        items['&Sort'] = OrderedDict()
        items['&Sort']['&Peptide'] = {
            'statusTip': 'Sort Transitions by Peptide',
            'triggered': partial(self.nodes.sort, 'Peptide')
        }
        items['&Sort']['&Retention Time'] = {
            'statusTip': 'Sort Transitions by RT',
            'triggered': partial(self.nodes.sort, 'RT')
        }
        items['&Sort']['&Peptide Score'] = {
            'statusTip': 'Sort Transitions by Peptide Score',
            'triggered': partial(self.nodes.sort, 'Score')
        }
        items['&Sort']['&Expectation Value'] = {
            'statusTip': 'Sort Transitions by EV',
            'triggered': partial(self.nodes.sort, 'EV')
        }
        items['&Sort']['&Mod Counts'] = {
            'statusTip': 'Sort Transitions by mod counts',
            'triggered': partial(self.nodes.sort, 'Mod Count')
        }

        items['&Peak Bounds'] = OrderedDict()
        items['&Peak Bounds']['&Start'] = OrderedDict()
        items['&Peak Bounds']['&Start']['&Left'] = {
            'statusTip': 'Move Start Bound Left',
            'shortcut': 'Alt+h',
            'triggered': partial(self.tree.line.move, 'start', -1, 1)
        }
        items['&Peak Bounds']['&Start']['&Strong Left'] = {
            'statusTip': 'Move Start Bound Strongly Left',
            'shortcut': 'Alt+Shift+h',
            'triggered': partial(self.tree.line.move, 'start', -1, 5)
        }
        items['&Peak Bounds']['&Start']['&Right'] = {
            'statusTip': 'Move Start Bound Right',
            'shortcut': 'Alt+j',
            'triggered': partial(self.tree.line.move, 'start', 1, 1)
        }
        items['&Peak Bounds']['&Start']['&Strong Right'] = {
            'statusTip': 'Move Start Bound Strongly Right',
            'shortcut': 'Alt+Shift+j',
            'triggered': partial(self.tree.line.move, 'start', 1, 5)
        }

        items['&Peak Bounds']['&End'] = OrderedDict()
        items['&Peak Bounds']['&End']['&Left'] = {
            'statusTip': 'Move End Bound Left',
            'shortcut': 'Alt+k',
            'triggered': partial(self.tree.line.move, 'end', -1, 1)
        }
        items['&Peak Bounds']['&End']['&Strong Left'] = {
            'statusTip': 'Move End Bound Strongly Left',
            'shortcut': 'Alt+Shift+k',
            'triggered': partial(self.tree.line.move, 'end', -1, 5)
        }
        items['&Peak Bounds']['&End']['&Right'] = {
            'statusTip': 'Move End Bound Right',
            'shortcut': 'Alt+l',
            'triggered': partial(self.tree.line.move, 'end', 1, 1)
        }
        items['&Peak Bounds']['&End']['&Strong Right'] = {
            'statusTip': 'Move End Bound Strongly Right',
            'shortcut': 'Alt+Shift+l',
            'triggered': partial(self.tree.line.move, 'end', 1, 5)
        }

        items['&Checkstate'] = OrderedDict()
        items['&Checkstate']['&Item'] = {
            'statusTip': 'Toggle Item',
            'shortcut': 'Space',
            'triggered': self.toggle.item
        }
        items['&Checkstate']['&Children'] = {
            'statusTip': 'Toggle Children',
            'shortcut': 'Shift+Space',
            'triggered': self.toggle.children
        }
        items[len(items)] = None

        items['&Settings'] = {
            'statusTip': 'Edit user settings',
            'triggered': self.settings
        }

        self.set_items(menu, items)

    def export(self, menu):
        '''Adds a menu for custom exportation settings'''

        items = OrderedDict()
        items['&Report'] = OrderedDict()
        items['&Report']['&Integrated'] = {
            'statusTip': 'Export Integrated',
            'shortcut': 'Ctrl+e',
            'triggered': partial(self.io.save_spreadsheet,
                self.tree.export.integrate),
        }
        items['&Report']['&Area'] = {
            'statusTip': 'Export Area List',
            'shortcut': 'Ctrl+Shift+e',
            'triggered': partial(self.io.save_spreadsheet,
                self.tree.export.area),
        }
        items['&Report']['&Intensity'] = {
            'statusTip': 'Export Intensity List',
            'shortcut': 'Ctrl+Alt+e',
            'triggered': partial(self.io.save_spreadsheet,
                self.tree.export.intensity),
        }

        items['&Report']['&Comparative'] = OrderedDict()
        items['&Report']['&Comparative']['&Standard'] = {
            'statusTip': 'Export Standard Quantitative Comparative',
            'triggered': partial(self.io.save_spreadsheet,
                self.tree.export.comparative),
        }
        items['&Report']['&Comparative']['&Filtered'] = {
            'statusTip': 'Export Filtered Quantitative Comparative',
            'triggered': partial(self.io.save_spreadsheet,
                self.tree.export.filteredcomparative),
        }

        items['&Report']['&Ratio Table'] = OrderedDict()
        items['&Report']['&Ratio Table']['&Standard'] = {
            'statusTip': 'Export Standard Ratio Table',
            'triggered': partial(self.io.save_spreadsheet,
                self.tree.export.ratiotable),
        }

        items['&Report']['&Ratio Table']['&Filtered'] = {
            'statusTip': 'Export Filtered Ratio Table',
            'triggered': partial(self.io.save_spreadsheet,
                self.tree.export.filteredratiotable),
        }

        self.set_items(menu, items)

    #    HELPERS

    def settings(self):
        settings.SettingsDialog(self.parent).exec_()
