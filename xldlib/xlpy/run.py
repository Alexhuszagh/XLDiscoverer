'''
    XlPy/run
    ________

    Runtime thread for XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division, print_function

# load modules
import inspect
import pdb
import sys
import time
import traceback

from PySide import QtCore

from xldlib import exception
from xldlib.objects import documents, matched, protein, run
from xldlib.onstart import args
from xldlib.qt.objects import threads
from xldlib.resources.parameters import defaults
from xldlib.utils import logger
from xldlib.utils.io_ import high_level

from . import files, helper, ms1quantitation, parameters


# CLASSES
# -------

CLASSES = [
    ('rundata', run.RunDataset),
    ('matched', matched.File)
]


# QTHREAD
# -------


@logger.init('threading', 'DEBUG')
class CrosslinkDiscovererThread(threads.BaseThread):
    '''
    Core thread which performs key tasks for Xl Discoverer
    Procedure:
        -- Verifies/processes inputs for running
        -- Iteratively scans inputs
    '''

    # SIGNALS
    # -------
    part_done = QtCore.Signal(int)
    procedure_done = QtCore.Signal(int)
    paused = QtCore.Signal(str)
    message = QtCore.Signal(str, str, bool)
    error = QtCore.Signal(object, list)

    def __init__(self, parent, quantitative=False):
        super(CrosslinkDiscovererThread, self).__init__(parent)

        self.quantitative = quantitative
        self.reporterions = defaults.DEFAULTS['reporterion_quantitation']

        self.proteins = protein.ProteinTable(tryopen=True, set_mapping=True)
        self.protein_model = protein.ProteinModel(None, self.proteins.db)
        self.parameters = parameters.Parameters()
        self.fingerprinting = self.proteins.get_limited()

        self.matched = matched.File.new()
        self.rundata = run.RunDataset(quantitative, new=True)

        if self.fingerprinting:
            self.mowse = protein.MowseDatabase.fromproteins(self.proteins)
        if self.quantitative:
            self.transitions = documents.TransitionsDocument.new()

        self.files = files.IntegratedFiles()
        self.helper = helper.RunHelper()

    def run(self):
        '''On start'''

        self.isrunning = True
        try:
            self.main()
            self.rundata.close()

        except IOError as msg:
            self.error.emit(Exception, msg)
        except StopIteration:
            self.error.emit(Exception, exception.CODES['010'])
        except Exception as error:
            if args.DEBUG:
                pdb.post_mortem()

            trace = traceback.format_exc()
            print(trace, file=sys.stderr)
            self.error.emit(error, exception.CODES['019'])

        finally:
            high_level.remove_tempfiles()

        self.isrunning = False
        self.procedure_done.emit(True)
        time.sleep(0.1)

    #     HELPERS

    def main(self):
        '''
        Iterates sequentially over the main functions to complete link
        discovery and data processing (as well as visualization).
        '''

        for caller in self.helper:
            time.sleep(0.05)
            if self.isrunning:
                if inspect.isclass(caller):
                    inst = caller()
                    inst()

                elif callable(caller):
                    caller()

    @logger.call('threading', 'debug')
    def pause(self, mode):
        '''Pauses the worker thread until an unpaused signal is emitted'''

        if self.isrunning:
            self.ispaused = True
            self.paused.emit(mode)

            while self.ispaused:
                time.sleep(0.01)

    @logger.call('threading', 'debug')
    def unpause(self, mode):
        '''Unpauses the worker thread to restart thread execution'''

        if mode == 'transition':
            inst = ms1quantitation.IntegrateXics.fromthread()
            inst()

        self.ispaused = False
