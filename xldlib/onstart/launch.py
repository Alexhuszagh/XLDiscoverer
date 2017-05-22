'''
    Onstart/launch
    ______________

    Methods to launch XL Discoverer, along with all the custom imports.
    Command line usage or multiprocessing modules should avoid this
    and gui/.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import print_function

# load modules
import sys

from . import args
from . import check_imports

# MAIN CHECK
# ----------

# Force quit if no PySide installation, IE, no GUI can be displayed.

if check_imports.MISSING and check_imports.MISSING[0].name == 'PySide':
    # need to sys exit
    print(check_imports.MISSING[0].message, file=sys.stderr)
    sys.exit(1)

from . import main


# CONDITIONAL IMPORTS
# -------------------

from . import error
from xldlib.resources import paths
from xldlib.resources.parameters import defaults
from xldlib.utils import logger


# INITIATE LOGGERS
# ----------------

HANDLERS = [
    'bio',
    'canvas',
    'chemical',
    'crosslinking',
    'database',
    'document',
    'gui',
    'linking',
    'matched',
    'modifications',
    'mowse',
    'object',
    'peakpicking',
    'quantitative',
    'report',
    'scans',
    'spreadsheet',
    'threading',
    'xlpy'
]

LOGGER = logger.Logging(paths.FILES['logger'], args.LOG)
for name in HANDLERS:
    LOGGER.add_logger(args.LOG, name)

if defaults.DEFAULTS['send_logs']:
    logger.Logging.add_remote(args.REMOTE_THRESHOLD)
LOGGER.add_streaming('INFO', 'stdout', retain=args.STDOUT)
LOGGER.add_streaming('WARN', 'stderr', retain=args.STDERR)


# CHECK IMPORTS
# -------------


def force_exit(missing):
    '''Force system exit if missing import after QDialog.exec_()'''

    dialog = error.ImportErrorDialog(missing.message)
    dialog.exec_()
    sys.exit(1)


def check_missing():
    '''Force exit for any missing, essential imports'''

    for missing in check_imports.MISSING:
        if missing.name in check_imports.REQUIRED:
            force_exit(missing)

        elif missing.name in check_imports.EXCEL_SWITCH:
            check_imports.SWITCH[missing.name].remove(missing.name)

            if not check_imports.SWITCH[missing.name]:
                # all the complementary imports have been exhausted
                force_exit(missing)


check_missing()


# SET ABCS
# --------

from . import registers
del registers


# LOAD GUI
# --------

from xldlib.gui.views.windows import splash


def window():
    '''Main app'''

    splash.SplashWindow()
    status = main.APP.exec_()
    sys.exit(status)
