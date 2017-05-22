'''
    Controllers/Bindings/decorators
    _______________________________

    Class with designed inheritance for copy/paste methods.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib.definitions import partial
from xldlib.qt.objects import threads
from xldlib.qt import resources as qt


# FUNCTIONS
# ---------


def newspinner(slot):
    '''
    Flanks a function call with a spinner show/hide event,
    and calls any main-thread events solely within the main-loop.
    '''

    def decorator(f):
        def newf(self, *args, **kwds):
            if self.app.threads:
                # task currently occuring, avoid tandem I/O
                return

            frozen = partial(f, self, *args, **kwds)
            blocked = partial(self.table.block_once, frozen)
            getattr(self.table, "showspinner", self.table.show)()

            worker = threads.WorkerThread(blocked)
            background = threads.BackgroundThread(worker, self)

            endfun = getattr(self.table, "hidespinner", self.table.show)
            worker.procedure_done.connect(endfun, qt.CONNECTION['Queued'])
            worker.result.connect(slot, qt.CONNECTION['Queued'])

            for thread in (worker, background):
                thread.start()

        return newf
    return decorator

def spinner(f):
    '''Flanks a function call with a spinner show/hide event'''

    def decorator(self, *args, **kwds):
        if self.app.threads:
            # task currently occuring, avoid tandem I/O
            return

        frozen = partial(f, self, *args, **kwds)
        blocked = partial(self.table.block_once, frozen)
        getattr(self.table, "showspinner", self.table.show)()

        worker = threads.WorkerThread(blocked)
        background = threads.BackgroundThread(worker, self)

        endfun = getattr(self.table, "hidespinner", self.table.show)
        worker.procedure_done.connect(endfun, qt.CONNECTION['Queued'])
        #worker.result.connect(slot)

        for thread in (worker, background):
            thread.start()

    decorator.__name__ = f.__name__
    return decorator
