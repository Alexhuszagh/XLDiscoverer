'''
    Views/Menus/fingerprint
    _______________________

    Sets the menu for a Peptide Mass Fingerprint visualizer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from . import base

# load objects/functions
from collections import OrderedDict

from xldlib.definitions import partial


# OBJECTS
# -------


class FingerprintMenu(base.BaseMenu):
    '''Adds a peptide mass fingerprint menu to the FingerprintWindow'''

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
            'statusTip': 'Open PMFs',
            'triggered': self.parent.io.open
        }
        items['&Open']['&Add'] = {
            'shortcut': 'Ctrl+Shift+A',
            'statusTip': 'Add PMFs',
            'triggered': partial(self.parent.io.open, mode='add')
        }

        items['&Save'] = {
            'shortcut': 'Ctrl+S',
            'statusTip': 'Save PMFs',
            'triggered': self.parent.io.save
        }
        items['&Save As'] = {
            'shortcut': 'Ctrl+Shift+S',
            'statusTip': 'Save PMF As',
            'triggered': self.parent.io.saveas
        }
        items['&Save File(s)'] = {
            'statusTip': 'Save PMF File(s)',
            'triggered': self.parent.io.save_files
        }
        items['&Save Image'] = {
            'shortcut': 'Ctrl+I',
            'statusTip': 'Save Current Image',
            'triggered': self.parent.io.save_image
        }

        items[len(items)] = None

        items['&Close'] = OrderedDict()
        items['&Close']['&All'] = {
            'statusTip': 'Close All File(s)',
            'shortcut': 'Ctrl+C',
            'triggered': self.parent.io.close_files
        }
        items['&Close']['&File(s)'] = {
            'statusTip': 'Close Selected File(s)',
            'shortcut': 'Ctrl+Shift+C',
            'triggered': self.parent.io.close_selected_files
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
            'triggered': partial(self.parent.nodes.sort, 'peptide')
        }
        items['&Sort']['&Retention Time'] = {
            'statusTip': 'Sort Transitions by RT',
            'triggered': partial(self.parent.nodes.sort, 'RT')
        }
        items['&Sort']['&Peptide Score'] = {
            'statusTip': 'Sort Transitions by Peptide Score',
            'triggered': partial(self.parent.nodes.sort, 'score')
        }
        items['&Sort']['&Expectation Value'] = {
            'statusTip': 'Sort Transitions by EV',
            'triggered': partial(self.parent.nodes.sort, 'EV')
        }
        items['&Sort']['&Mod Counts'] = {
            'statusTip': 'Sort Transitions by mod counts',
            'triggered': partial(self.parent.nodes.sort, 'Mod Count')
        }

        items[len(items)] = None

#        items['&Checkstate'] = OrderedDict()
#        items['&Checkstate']['&Item'] = {
#            'statusTip': 'Toggle Item',
#            'shortcut': 'Space',
#            'triggered': self.parent.tree.toggle_item
#        }
#        items['&Checkstate']['&Children'] = {
#            'statusTip': 'Toggle Children',
#            'shortcut': 'Shift+Space',
#            'triggered': self.parent.tree.toggle_children
#        }
#
#        items[len(items)] = None
#
#        items['&Annotations'] = {
#            'statusTip': 'Edit Annotations',
#            'shortcut': 'Ctrl+A',
#            'triggered': self.parent.change_labels
#        }

        self.set_items(menu, items)

    def export(self, menu):
        '''Adds a menu for custom exportation settings'''

        items = OrderedDict()
        items['&Report'] = OrderedDict()

        self.set_items(menu, items)

