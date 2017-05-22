'''
    XlPy/Matched/scan_titles
    ________________________

    Processing Mascot modnames depending on the UniMod specification.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
from xldlib import resources
from xldlib.definitions import re
from xldlib.qt.objects import base


# REGEXES
# -------

PARSERS = [re.compile(i.regexp) for i in resources.SCAN_TITLES]


# MATCHER
# -------


class TitleFormatter(base.BaseObject):
    '''
    Identify the scan title format based on regex matches, otherwise
    raise an `AssertionError`. After identifying the title format,
    use the title formatter to extract the scan number from
    scan filters.
    '''

    def __init__(self):
        super(TitleFormatter, self).__init__()

    def __call__(self, title):
        '''Parse `title` and return the scan number'''

        if not hasattr(self, "parser"):
            self._set_parser(title)
        return self.parser.match(title)

    #     SETTERS

    def _set_parser(self, title):
        '''Identify title parser to extract scan metadata'''

        for parser in PARSERS:
            match = parser.match(title)
            if match is not None:
                self.parser = parser
                break
        else:
            raise AssertionError("No suitable parser found")
