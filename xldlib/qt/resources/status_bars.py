'''
    Qt/Resources/status_bars
    ________________________

    Element definitions for status_bars.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from namedlist import namedlist

__all__ = [
    'INPUT_TABLE_BAR',
    'TABLE_BAR',
    'TRANSITIONS_BAR'
]

# OBJECTS
# -------

Shortcut = namedlist("Shortcut", "key sequence description")

# DATA
# ----

#MENU = [
#    Shortcut(key='Ctrl+F4', description='Close Application'),
#    Shortcut(key='Ctrl+s', description='Save Settings')
#]
#

TABLE_BAR = [
    Shortcut(key='A',
        sequence='Ctrl + A',
        description='Select All'),
    Shortcut(key='B',
        sequence='Ctrl+ B',
        description='Block Signals'),
    Shortcut(key='C',
        sequence='Ctrl + C',
        description='Copy Cells'),
    Shortcut(key='E',
        sequence='Ctrl + Shift + E',
        description='Extended Selection'),
    Shortcut(key='F',
        sequence='Ctrl + F',
        description='Find/Replace Cells'),
    Shortcut(key='M',
        sequence='Ctrl + Shift + M',
        description='Multi Selection'),
    Shortcut(key='S',
        sequence='Ctrl+ S',
        description='Save Settings'),
    Shortcut(key='S',
        sequence='Ctrl + Shift + S',
        description='Single Selection'),
    Shortcut(key='V',
        sequence='Ctrl + V',
        description='Paste'),
    Shortcut(key='X',
        sequence='Ctrl + X',
        description='Cut'),
    Shortcut(key='Del',
        sequence='Del',
        description='Delete'),
]

INPUT_TABLE_BAR = TABLE_BAR + [
    Shortcut(key='Enter',
        sequence='Enter',
        description='Select File'),
]

TRANSITIONS_BAR = [
    Shortcut(key='A',
        sequence='Ctrl + Shift + A',
        description='Add File'),
    Shortcut(key='C',
        sequence='Ctrl + C',
        description='Close All'),
    Shortcut(key='C',
        sequence='Ctrl + Shift + C',
        description='Close Selected'),
    Shortcut(key='H',
        sequence='Alt + H',
        description='Move Start Left'),
    Shortcut(key='I',
        sequence='Ctrl + I',
        description='Save Image'),
    Shortcut(key='J',
        sequence='Alt + J',
        description='Move Start Right'),
    Shortcut(key='K',
        sequence='Alt + K',
        description='Move End Left'),
    Shortcut(key='L',
        sequence='Alt + L',
        description='Move End Right'),
    Shortcut(key='O',
        sequence='Ctrl + O',
        description='Open file'),
    Shortcut(key='S',
        sequence='Ctrl + S',
        description='Save'),
    Shortcut(key='S',
        sequence='Ctrl + Shift + S',
        description='Save As'),
    Shortcut(key='Left',
        sequence='Left',
        description='Collapse Node'),
    Shortcut(key='Left',
        sequence='Shift + Left',
        description='Expand From Node'),
    Shortcut(key='Right',
        sequence='Right',
        description='Expand Node'),
    Shortcut(key='Space',
        sequence='Space',
        description='Check Item'),
    Shortcut(key='Space',
        sequence='Shift + Space',
        description='Check From Item'),
]
