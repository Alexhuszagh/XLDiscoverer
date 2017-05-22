'''
    XlPy/helper
    ___________

    Helper for runtime execution.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import six
import types
import weakref

from xldlib import exception
from xldlib.export import openoffice, spreadsheet
from xldlib.qt.objects import base
from xldlib.utils import logger

from . import (counts, inputs, link_finder, matched, ms1quantitation,
               productquantitation, scan_linkers, spectra)

# HELPERS
# -------


@logger.init('xlpy', 'DEBUG')
class RunHelper(base.BaseObject):
    '''
    Temporary storage setter and getter. The data must be specific to the
    given run, and must not be required after the run is finished,
    and must be required by multiple utilities.
    '''

    def __init__(self):
        super(RunHelper, self).__init__()

        self.source = weakref.proxy(self.app.discovererthread)
        self.counts = counts.TotalCounts()
        self.set_callables()

    def __iter__(self):
        return iter(self.callables)

    #     SETTERS

    def set_callables(self):
        '''Sets the runtime callables'''

        self.callables = (
            inputs.checkinputs,
            self.source.files.parsematched,
            matched.calculateformulas,
            matched.addnames,
            spectra.parsespectra,
            scan_linkers.linkprecursor,
            self.source.files.deleteignored,
            self.source.files.update,
            link_finder.calculatelinks,
            productquantitation.quantifyreporterions,
            spreadsheet.createspreadsheets,
            ms1quantitation.findisotopelabeled,
            ms1quantitation.extractms1,
            ms1quantitation.linkms1,
            ms1quantitation.processxics,
            openoffice.writematched
        )

    #     HELPERS

    def emitsequence(self, message, sequence, color="red", bool_=True):
        '''Pluralizes and emits sequential data to the worker thread'''

        pluralized = exception.convert_number(message, sequence)
        string = ', '.join([str(i) for i in sequence])
        formatted = pluralized.format(string)
        self.source.message.emit(formatted, color, bool_)
