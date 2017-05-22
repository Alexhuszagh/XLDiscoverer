'''
    XlPy/Matched/base
    _________________

    Inheritable class with methods shared by all parsed data sets,
    to remove decoys, crosslinker-less peptides, and store
    unique UniProt KB IDs or mnemonics.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.qt.objects import base

from . import remove


# OBJECTS
# -------


class MatchedPeptideBase(base.BaseObject):
    '''Base class for matched peptides, providing methods for inheritance'''

    def __init__(self, row):
        super(MatchedPeptideBase, self).__init__()

        self.row = row
        self.fileobj = open(row.files['matched'])

        self.remove = remove.RemoveIds(row)

    #     SETTERS

    def setids(self):
        '''
        Stores unique UniProt KB IDs grouped by MS3 scan. Grabs
        all MS3 scans, sorts them by scan, uses itertools groupby and
        extracts the IDs for all scans within a single ID.
        '''

        source = self.app.discovererthread
        unique = sorted(set(self.row.data['matched']['id']))
        if source.matched.getattr('fingerprinting'):
            # then need to filter those not in filtered db
            ids = source.proteins.mapping['proteins']
            unique = [i for i in unique if i in ids]

        self.row.data['attrs']['uniqueids'] = unique
