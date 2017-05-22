'''
    XlPy/Spectra/link
    _________________

    Parser for the PAVA .link file format, which is a tab-delimited
    text format with the precursor and product ion scan numbers and
    retention times.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from collections import OrderedDict

from xldlib.qt.objects import base
from xldlib.utils import decorators, logger

# PARSERS
# -------

LINK = OrderedDict([
    ('retention_time', [1, float]),
    ('precursor_num', [2, int]),
    ('precursor_rt', [3, float]),
])


# OBJECTS
# -------


@logger.init('scans', level='DEBUG')
class ParseText(base.BaseObject):
    '''Processes mod strings to dictionary from file object'''

    # DELIMITERS
    # ----------
    delimiter = '\t'

    @decorators.overloaded
    def __init__(self, fileobj, group):
        super(ParseText, self).__init__()

        self.fileobj = fileobj
        self.group = group
        self.source = self.app.discovererthread

    @logger.raise_error
    def __call__(self):
        '''On start. Parses line-by-line'''

        self.fileobj.readline()
        for line in self.fileobj:
            self.process_data(line.strip())
        self.fileobj.close()

    def process_data(self, scan_csv):
        '''
        Process a single, linked MS scan and stores the data in
        self.data. Stores the linked scan numbers.
        '''

        scan = scan_csv.split(self.delimiter)

        num = int(scan[0])
        group = self.source.rundata.create.scan(self.group, num)
        group._v_attrs.num = num

        for key, (position, typecast) in LINK.items():
            setattr(group._v_attrs, key, typecast(scan[position]))
