'''
    Gui/Views/Visualizer/IO_/transition
    ___________________________________

    Input/output methods for a transitions document.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from PySide import QtCore, QtGui

from . import base
from xldlib.objects.documents import transitions
from xldlib.utils import logger


# HELPERS
# -------


def processevents(f):
    '''Update the GUI between each function call'''

    def decorator(self, *args, **kwds):
        self.app.processEvents()
        return f(self, *args, **kwds)

    decorator.__name__ = f.__name__
    return decorator


# I/O
# ---


@logger.init('document', 'DEBUG')
class TransitionIo(base.BaseIo):
    '''
    Provides methods for processing I/O events for extracted ion
    chromatograms from a QTreeView widget, with the document being
    the PyTables spectral document, and the model being the
    QStandardItemModel for the QTreeView.
    '''

    def __init__(self, parent):
        super(TransitionIo, self).__init__(parent, fileformat='transition')

    #   PUBLIC FUNCTIONS

    #    INITIALIZERS

    @logger.call('document', 'debug')
    @processevents
    def populate(self, document):
        '''Initializes a file node in the transitions file'''

        if document is not None:
            self.stylizer.setattrs()

            for transition_file in document:
                self.set_file(transition_file)

    #      SETTERS

    @processevents
    def set_file(self, transition_file):
        '''Initializes a file node in the transitions file'''

        node = QtGui.QStandardItem(transition_file.search)
        node.setData(transition_file.levels)

#        # TODO: remove line >>>>>>>
#        from xldlib.xlpy.tools.xic_picking import ab3d, fit, xicfit
#        selection = fit.ToggleSelection()
        #filtered = fit.FilterIsotopicLabels()
#        # <<<<<<<<<<<
        for labels in transition_file:
#            # TOOD: REMOVE >>>>>>>>>>>
#            fits = map(xicfit.get_fitargs, filtered(labels))
#            bounds = map(ab3d.boundab3d, fits)
#            bound = next(bounds)
#            labels.setattr('peak_start', bound.start)
#            labels.setattr('peak_end', bound.end)
#            labels.calculate_fit()
#            selection(labels)
#            # <<<<<<<<<<<<<<
            child = self.set_labels(labels)
            node.appendRow(child)

        self.model().appendRow(node)

    @processevents
    def set_labels(self, labels):
        '''Initializes a labels node in the transitions file'''

        name = self.stylizer.peptides(labels)
        node = self.get_child(name, checkstate=False)
        node.setData(labels.levels)

        for crosslink in labels:
            child = self.set_crosslink(crosslink)
            node.appendRow(child)

        return node

    @processevents
    def set_crosslink(self, crosslink):
        '''Initializes a crosslink node in the transitions file'''

        name = self.stylizer.crosslinks(crosslink)
        node = self.get_child(name)
        node.setData(crosslink.levels)
        self.set_checkstate(node, crosslink)

        for charge in crosslink:
            child = self.set_charge(charge)
            node.appendRow(child)

        return node

    @processevents
    def set_charge(self, charge):
        '''Initializes a charge node in the transitions file'''

        node = self.get_child(str(charge.levels.charge))
        node.setData(charge.levels)
        self.stylizer(node, charge)
        self.set_checkstate(node, charge)

        for index, isotope in enumerate(charge):
            child = self.set_isotope(index, isotope)
            node.appendRow(child)

        return node

    @processevents
    def set_isotope(self, index, isotope):
        '''Initializes an isotope node in the transitions file'''

        node = self.get_child(str(index))
        node.setData(isotope.levels)
        self.stylizer(node, isotope)
        self.set_checkstate(node, isotope)

        return node

    @staticmethod
    def set_checkstate(item, group):
        '''
        Set the checkstate for a given item from the 'checked' value
        of the dictionary holder.
        '''

        if group.checked:
            item.setCheckState(QtCore.Qt.CheckState(2))
        else:
            item.setCheckState(QtCore.Qt.CheckState(0))

    #     HELPERS

    def checkattrs(self, newdocument):
        '''Ensure new document has same crosslinker/profile'''

        # ensure the two files have the same extraction parameters
        for key in transitions.DOCUMENT_ATTRS:
            assert getattr(self.document, key) == getattr(newdocument, key)
