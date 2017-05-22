'''
    XlPy/Tools/Modtools/isotopic_labels
    ___________________________________

    Processes the crosslinker labels based on the isotope profile

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from xldlib.general import sequence
from xldlib.qt.objects import base
from xldlib import resources
from xldlib.resources.parameters import defaults
from xldlib.utils import logger


# LABELER
# -------


@logger.init('modifications', 'DEBUG')
class ModificationLabeler(base.BaseObject):
    '''
    Finds all labels associated with each peptide in a crosslink,
    joins them and returns the resulting labels to string.
    '''

    # DELIMITERS
    # ----------
    sep = ' - '
    hybrid = '+'

    def __init__(self, row):
        super(ModificationLabeler, self).__init__()

        self.setlabels(row)

    def __call__(self, modifications, join=True):
        '''
        Labels all the modifications and then
            modifications -- list of mod dictionaries
            join -- bool for whether to join via the seperator
        '''

        labeled = sorted(self.getlabels(modifications))
        if join:
            return self.sep.join(labeled)
        else:
            return labeled

    #    SETTERS

    def setlabels(self, row):
        '''Sets the isotopic modification names and labels'''

        name, version = row.data['attrs']['engines']['matched']
        self.labels = resources.ISOTOPIC_LABELS.get(name, {}).get(version, {})

    #    GETTERS

    def getlabels(self, modifications):
        '''Returns all the peptide labels from their modifications'''

        for modification in modifications:
            labels = sorted(self.getisotopiclabels(modification))
            if not labels:
                yield defaults.DEFAULTS['default_isotopic_label']
            else:
                yield self.hybrid.join(sequence.uniquer(labels))

    def getisotopiclabels(self, modification):
        '''
        Finds all mod labels within a mod dictionary and returns a list
        of labels. Typically used with isotopic labels.
        '''

        if hasattr(modification, "unpack"):
            modification = modification.unpack()

        for name in modification:
            if name in self.labels:
                yield self.labels[name]
