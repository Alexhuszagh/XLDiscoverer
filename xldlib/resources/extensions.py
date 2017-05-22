'''
    Resources/extensions
    ____________________

    Stores meaningful file extensions through a namedlist type.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load objects/functions
from namedlist import namedlist


__all__ = [
    'SESSION',
    'SPREADSHEET',
    'TRANSITIONS',
    'FINGERPRINT',
    'PNG',
    'SQLITE',
    'JSON',
    'RAW'
]

# OBJECTS
# -------

Extension = namedlist("Extension", "filetype extension")


# EXTENSIONS
# ----------

# CUSTOM
# ------
SESSION = Extension("Sessions", 'pkl')
TRANSITIONS = Extension("Transitions", 'xld')
FINGERPRINT = Extension("Fingerprints", 'pmf')

# SPREADSHEET
# -----------
SPREADSHEET = Extension("Spreadsheets", 'xlsx')

# IMAGES
# ------
PNG = Extension("Image Files", 'png')

# DATABASE/STORAGE
# ----------------
SQLITE = Extension("SQLite", 'sqlite')
JSON = Extension("JSON", 'json')

# SPECTRAL
# --------

RAW = Extension("Spectral Files", (
    "mzXML",
    "mzML",
    "txt",
    "mgf",
    "raw",
    "mzData",
    "mzIdentML",
    "xml",
    "gz",
    "bz2"
))
