'''
    Exceptions/codes
    ________________

    Organized error codes for reporting errors and exceptions.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

CODES = {
    "000": ("Cannot find file%(-s)s in row%(-s)s {0}."
            " Deleting th%(-at)s entr%(-y)s..."),
    "001": ("File%(-s)s in row%(-s)s {0} not recognized."
            " Deleting th%(-at)s entr%(-y)s..."),
    "002": ("Engine in row%(-s)s {0} do not match the isotope-label profile."
            " Deleting th%(-at)s entr%(-y)s..."),

    "003": ("Files in row%(-s)s {0} do not have matching MS2/MS3 scans. "
            "Deleting those entries..."),
    "004": ("Some columns are missing data.", "WARNING: Missing data"),
    "005": ("The content of the clipboard is bigger than available "
            "space.\nSome data loss will occur. Still want to paste?",
            "WARNING: Data clipping"),
    "006": ("The content of the clipboard is bigger or smaller than "
            "the range selected.\nStill want to paste?",
            "WARNING: Data clipping"),
    "007": "Calculations are running. Are you sure you want to close?",
    "008": ("Input Error", "Unequal number of files entered"),
    "009": ("Truncated mod found from Protein Prospector. "
            "Please check your report settings."),
    "010": ("Parser Error", "Malfunctioning parser unable to match "
            "scan row. Please contact {}"),
    "011": ("Warning: Data for MS3 scan%(-s)s {{}} in file {} do not "
            "have matching MS2 precursors. This data was removed..."),
    "012": ("Input Error", "ERROR: Please select a cross-linker "
            "before running Xl Discoverer."),
    "013": ("Input Error", "Cannot find the path specified"),
    "014": ("Gradient times are not close enough to analyze the same "
            "transition over multiple files. Turning global quantitation "
            "off."),
    "015": ("Files in row%(-s)s {0} do not have any searchable matched "
            "peptides. Deleting those entries..."),
    "016": ("Input Error", "Likely truncated MS3 scan detected. "
            "Invalid (blank) entry in Matched Output."),
    "017": ("Input Error", "Invalid entry in Matched Output."),
    "018": ("Parser Error", "Malfunctioning parser cannot parse "
            "scan data. Please contact alexhuszagh@gmail.com"),
    "019": ("Error", "An unknown error occured, please check the log file"),
    "020": ("Input Error", "Selected cross-linkers do not match the "
            "selected isotopic profile."),
    "021": ("The sort data does not exist in the transitions "
            "file and therefore cannot be sorted.", "Sorting Error"),
    "022": "{0} column%(-s)s missing in current matched scans file",
    "023": ("Input Error", "Could not recognize the spectral file entered."),
    "024": ('Please add the chemical formula for "{}" to xlpy/matched/'
            'proteome_discoverer/mods.py in MONOMERS'),
    "025": ("Warning: Protease specified in matched output and was not found "
            "in local protease list."),
    "026": ("Some entered files do not exist", "WARNING: Missing data"),
}
