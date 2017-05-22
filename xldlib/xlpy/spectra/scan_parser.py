'''
    XlPy/Spectra/scan_parser
    ____________________

    Quick tool to split scan-delimited file formats (such as MGF) to
    allow parsing on entire scans without loading the full file
    into memory.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import six

from xldlib.definitions import re
from xldlib.qt.objects import base
from xldlib.utils import logger


# OBJECTS
# -------


@logger.init('scans', level='DEBUG')
class ScanFinder(base.BaseObject):
    '''
    Iteratively parses chunks and breaks them into scans, with
    a bound remainder.
    '''

    def __init__(self, start_sub, end_sub):
        super(ScanFinder, self).__init__()

        self.remainder = ''
        self.start_sub = start_sub
        self.end_sub = end_sub

    def __call__(self, chunk):
        '''
        Parses a read chunk and adds to the remainder, and then
        processes scan start and ends. For each scan found, separately
        processes the entire scan
        :
            chunk -- read chunk, ie, 4096 chars, etc.
            __call__('IONS\nFile....')->[{'num': 345, ...}, ...]
        '''

        self.remainder = ''.join([self.remainder, chunk])

        end = 0
        while end != -1:
            start = self.get_scan_start()
            end, match = self.get_scan_end()

            if end != -1:
                scan = self.get_scan(start, end, match)
                yield scan
                self.adjust_remainder(end, match)

    @classmethod
    def fromengine(cls, engine, start=False, end=False):
        '''Compiles the start and end subs and initializes the class'''

        startsub = engine.defaults.start
        if start:
            startsub = re.compile(startsub)

        endsub = engine.defaults.end
        if end:
            endsub = re.compile(endsub)
        return cls(startsub, endsub)

    #      GETTERS

    def get_scan_start(self):
        '''
        Finds the start position of a given scan
            get_scan_start()->1000
        '''

        if isinstance(self.start_sub, six.string_types):
            return self.remainder.find(self.start_sub)

        elif isinstance(self.start_sub, re._pattern_type):
            match = self.start_sub.search(self.remainder)
            if match is None:
                return -1
            else:
                return match.start()

    def get_scan_end(self):
        '''
        Finds the end position of a given scan.
            get_scan_end()->1303030
        '''

        if isinstance(self.end_sub, six.string_types):
            return self.remainder.find(self.end_sub), None

        elif isinstance(self.end_sub, re._pattern_type):
            match = self.end_sub.search(self.remainder)
            if match is None:
                return -1, match
            else:
                return match.start(), match

    def get_scan(self, start, end, match):
        '''
        Gets the full scan string of the MS scan file.
            start, end -- ints for start and end of the scan
            match -- re match pattern or NoneType
            get_scan(1000, 1303030)->"BEGIN IONS\n..."
        '''

        if isinstance(self.end_sub, six.string_types):
            sub_end = end + len(self.end_sub)

        elif isinstance(self.end_sub, re._pattern_type):
            sub_end = match.end()

        return self.remainder[start:sub_end]

    #      HELPERS

    def adjust_remainder(self, end, match):
        '''
        Adjusts the remaining string length for new scan processing.
            end -- ints for start and end of the scan
            match -- re match pattern or NoneType
        '''

        if isinstance(self.end_sub, six.string_types):
            sub_end = end + len(self.end_sub)

        elif isinstance(self.end_sub, re._pattern_type):
            sub_end = match.end()

        self.remainder = self.remainder[sub_end:]
