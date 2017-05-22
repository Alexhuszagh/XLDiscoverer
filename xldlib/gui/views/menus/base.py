'''
    Views/Menus/base
    ________________

    Inheritable menubar definition to facilitate menubar creation.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import os
import webbrowser

from PySide import QtGui

from xldlib.utils import logger

# load objects/functions
from collections import OrderedDict

from xldlib.definitions import partial

# OBJECTS
# -------


@logger.init('document', 'DEBUG')
class BaseMenu(object):
    '''Provides the base methods to add the menu items from dict'''

    def __init__(self, parent):
        super(BaseMenu, self).__init__()

        self.parent = parent

    #     PROPERTIES

    @property
    def tree(self):
        return self.parent.widget.tree

    @property
    def io(self):
        return self.parent.io

    @property
    def nodes(self):
        return self.parent.nodes

    @property
    def toggle(self):
        return self.parent.toggle

    #      SETTERS

    def set_items(self, menu, items):
        '''Adds all the items ito a QView'''

        for name, item in items.items():

            if item is None:
                menu.addSeparator()

            # menu entry
            elif isinstance(item, OrderedDict):
                newmenu = menu.addMenu(name)
                self.set_items(newmenu, item)

            # regular action
            else:
                action = QtGui.QAction(name, self.parent, **item)
                menu.addAction(action)

    #       MENUS

    def view(self, menu):
        '''Adds all the view entries to the widgets'''

        items = OrderedDict()
        items['&Expand'] = OrderedDict()
        items['&Expand']['&All'] = {
            'statusTip': 'Expand All',
            'shortcut': 'Ctrl+Shift+Right',
            'triggered': self.nodes.expand
        }
        items['&Expand']['&From Selected'] = {
            'statusTip': 'Expand From Selected',
            'shortcut': 'Shift+Right',
            'triggered': partial(self.nodes.expand, select=True,
                recurse=True)
        }
        items['&Expand']['&Selected'] = {
            'statusTip': 'Expand Selected',
            'shortcut': 'Right',
            'triggered': partial(self.nodes.expand, select=True)
        }

        items['&Collapse'] = OrderedDict()
        items['&Collapse']['&All'] = {
            'statusTip': 'Collapse All',
            'shortcut': 'Ctrl+Shift+Left',
            'triggered': self.nodes.collapse
        }
        items['&Collapse']['&From Selected'] = {
            'statusTip': 'Collapse From Selected',
            'shortcut': 'Shift+Left',
            'triggered': partial(self.nodes.collapse, select=True,
                recurse=True)
        }
        items['&Collapse']['&Selected'] = {
            'statusTip': 'Collapse Selected',
            'shortcut': 'Left',
            'triggered': partial(self.nodes.collapse, select=True)
        }

        self.set_items(menu, items)

    def graph(self, menu):
        '''Adds all the graph entries to the widgets'''

        items = OrderedDict()
        items['&Zoom'] = OrderedDict()
        items['&Zoom']['&In'] = {
            'statusTip': 'Zoom X-Axis In 10%',
            'shortcut': 'Ctrl++',
            'triggered': self.tree.zoom.zoomin
        }
        items['&Zoom']['&Out'] = {
            'statusTip': 'Zoom X-Axis Out 10%',
            'shortcut': 'Ctrl+-',
            'triggered': self.tree.zoom.zoomout
        }

        items['&Zoom'][len(items['&Zoom'])] = None

        items['&Zoom']['&Home'] = {
            'statusTip': 'Home View',
            'shortcut': 'Ctrl+h',
            'triggered': self.tree.zoom.home
        }
        items['&Zoom']['&Next'] = {
            'statusTip': 'Next View',
            'triggered': self.tree.zoom.next
        }
        items['&Zoom']['&Previous'] = {
            'statusTip': 'Previous View',
            'triggered': self.tree.zoom.previous
        }

        self.set_items(menu, items)

    def help(self, menu):
        '''Adds a custom menu for help items'''

        items = OrderedDict()
        url = 'https://github.com/Alexhuszagh/xlDiscoverer'
        doc = os.path.join(url, 'blob/master/Tutorial.md')
        items['&Documentation'] = {
            'statusTip': 'Read Documentation',
            'triggered': partial(webbrowser.open, doc)
        }
        items['&About'] = {
            'statusTip': 'About XL Discoverer',
            'triggered': self.parent.aboutdialog.show
        }
        items[len(items)] = None

        items['&License'] = {
            'statusTip': 'License Information',
            'triggered': self.parent.licensedialog.show
        }

        self.set_items(menu, items)
