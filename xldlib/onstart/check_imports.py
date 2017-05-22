'''
    Xldlib/Onstart/check_imports
    ____________________________

    Check imports before initializing XL Discoverer.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import importlib

# load objects/functions
from collections import namedtuple

from xldlib.definitions import partial

__all__ = [
    'check_version',
    'EXCEL_SWITCH',
    'MISSING',
    'Module',
    'REQUIRED',
    'yield_missing',
]

# OBJECTS
# -------

Module = namedtuple("Module", "name path condition message")


# MESSAGE
# -------

PYSIDE_MESSAGE = ("XL Discoverer requires a PySide installation, "
    "which can be found from https://pypi.python."
    "org/pypi/PySide or installed via pip.")

SIX_MESSAGE = ("XL Discoverer requires a six installation, which can "
    "be found from <a href='https://bitbucket.org/gutworth/six'>BitBucket</a>"
    " or installed via pip.")

SCIPY_MESSAGE = ("XL Discoverer requires a SciPy stack installation, "
    "which can be found from <a href='https://www.scipy.org'>scipy.org</a>. "
    "Numpy and SciPy are required.")

PYQTGRAPH_MESSAGE = ("XL Discoverer requires a PyQtGraph installation, "
    "which can be found from <a href='http://www.pyqtgraph.org'>"
    "pyqtgraph.org</a>.")

XLSXWRITER_MESSAGE = ("XL Discoverer requires an XlsxWriter installation "
    "which can be found at <a href='https://pypi.python.org/pypi/XlsxWriter'>"
    "PyPi</a>.")

OPENPYXL_MESSAGE = ("XL Discoverer requires an OpenPyXl installation, which "
    "can be found at <a href='https://pypi.python.org/pypi/openpyxl'>"
    "PyPi</a>.")

REQUESTS_MESSAGE = ("XL Discoverer requires a Requests installation, "
    "which can be found from <a href='http://docs.python-requests.org/'>"
    "docs.python-requests.org</a>")

TABLES_MESSAGE = ("XL Discoverer requires a PyTables installation, "
    "which can be found from <a href='http://www.pytables.org/'>"
    "pytables.org</a>. On windows, install a suitable binary from "
    "<a href='http://www.lfd.uci.edu/~gohlke/pythonlibs/'>here</a>.")

TESTFIXTURES_MESSAGE = ("XL Discoverer requires a testfixtures installation, "
    "which can found from <a href='https://pythonhosted.org/testfixtures/'>"
    "pythonhosted.org/testfixtures/</a>.")


# VERSIONING
# ----------

def check_version(version, module):
    '''
    Check all dependent versions are recent enough
        check_version((1, 7), numpy) -> True
    '''

    current = [i for i in module.__version__.split('.') if i.isdigit()]
    module_version = tuple(int(i) for i in current)
    return module_version >= version


# EXTERNAL DEPENDENCIES
# ---------------------

MODULES = (
    Module('PySide', 'PySide',
        condition=lambda x: True,
        message=PYSIDE_MESSAGE),
    Module('PySide', 'PySide.QtCore',
        condition=lambda x: True,
        message=PYSIDE_MESSAGE),
    Module('PySide', 'PySide.QtGui',
        condition=lambda x: True,
        message=PYSIDE_MESSAGE),
    Module('six', 'six',
        condition=lambda x: True,
        message=SIX_MESSAGE),
    Module('NumPy', 'numpy',
        condition=partial(check_version, (1, 7, 1)) ,
        message=SCIPY_MESSAGE),
    Module('PyQtGraph', 'pyqtgraph',
        condition=lambda x: True,
        message=PYQTGRAPH_MESSAGE),
    Module('SciPy', 'scipy',
        condition=lambda x: True,
        message=SCIPY_MESSAGE),
    Module('XlsxWriter', 'xlsxwriter',
        condition=lambda x: True,
        message=XLSXWRITER_MESSAGE),
    Module('OpenPyXl', 'openpyxl',
        condition=lambda x: True,
        message=OPENPYXL_MESSAGE),
    Module('Requests', 'requests',
        condition=lambda x: True,
        message=REQUESTS_MESSAGE),
    Module('PyTables', 'tables',
        condition=partial(check_version, (3, 2)) ,
        message=TABLES_MESSAGE),
    Module('TestFixtures', 'testfixtures',
        condition=lambda x: True ,
        message=TESTFIXTURES_MESSAGE),
)


# CHECK IMPORTS
# -------------


def yield_missing(modules=MODULES):
    '''Yield missing imports'''

    for module in modules:
        try:
            imported = importlib.import_module(module.path)
            assert module.condition(imported)
        except Exception:
            yield module

# CONSTANTS
# ---------

MISSING = list(yield_missing())

REQUIRED = {
    'PySide',
    'six',
    'NumPy',
    'pyqtgraph',
    'SciPy',
    'Requests',
    'PyTables',
}

EXCEL_SWITCH = {
    'OpenPyXl',
    'XlsxWriter'
}
SWITCH = {
    'XlsxWriter': EXCEL_SWITCH,
    'OpenPyXl': EXCEL_SWITCH
}
