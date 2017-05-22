'''
    Utils/IO_/high_level
    ____________________

    Methods for extracting/compressing zip archives and cleaning
    up temporary files.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import atexit
import os
import tempfile

from xldlib.onstart import app
from .. import decorators

# CONSTANTS
# ---------
TMP_DIR = tempfile.gettempdir()


# DECORATORS
# ----------


def tmpmemo(f):
    '''Memoizes the returns name and adds it the the QApplication's memo'''

    def decorator(*args, **kwds):
        path = f(*args, **kwds)
        app.App.temporary_files.add(path)
        return path

    decorator.__name__ = f.__name__
    return decorator


def remove_tmpmemo(f):
    '''Removes the path from the tempfile memo'''

    def decorator(path):
        if path in app.App.temporary_files:
            app.App.temporary_files.remove(path)
        f(path)

    decorator.__name__ = f.__name__
    return decorator


# HIGH LEVEL
# ----------


def touch(path):
    '''Analog of shell "touch"'''

    with open(path, 'w') as f:
        pass


@tmpmemo
def mkstemp():
    '''Returns a named, stable temporary file'''

    __, name = tempfile.mkstemp()
    os.close(__)
    return name


@remove_tmpmemo
def remove_file(name):
    '''
    Tries to remove a given fileobject, typically a temp file, with
    the knowledge that Windows prevents removing accessed files,
    which could be caused by any process.
    '''

    try:
        if os.path.exists(name):
            os.remove(name)

    # should be OSError, not WindowsError
    except OSError as err:
        if err.args[0] == 32:
            # Windows 32 error, cannot access file
            try:
                # try truncating it, accept and skip all errors
                fileobj = open(name, 'w')
                fileobj.close()
            except Exception:
                pass


def remove_tempfile(*paths):
    '''Removes a permanent tempfile, memoed by the QApplication.'''

    for path in paths:
        if path in app.App.temporary_files:
            remove_file(path)


def remove_tempfiles():
    remove_tempfile(*app.App.temporary_files)


# REGISTERS
# ---------

atexit.register(remove_tempfiles)
