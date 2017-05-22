'''
    XlPy/Matched/Mascot/core
    ________________________

    Objects which parse different Mascot file formats and are
    the engines the process the matched data.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# lod modules
import os
import xml.sax

from xldlib.utils import logger
from . import mime
from .. import base, pepxml


# PEPXML
# ------


@logger.init('matched', 'DEBUG')
class ParseXml(base.MatchedPeptideBase):
    '''Processes data from the pep.XML format of Mascot'''

    def __init__(self, row):
        super(ParseXml, self).__init__(row)

        self.handler = pepxml.PepXmlHandler(row)
        self.parser = xml.sax.make_parser()
        self.parser.setContentHandler(self.handler)

    def __call__(self):
        '''On start'''

        self.parser.parse(self.fileobj)
        self.fileobj.close()

        self.setids()
        self.setfileheader()

    #     SETTERS

    def setfileheader(self):
        '''
        Stores the project and search names identically since the
        search name is typically missing.
        '''

        fraction = os.path.basename(self.handler.start._fraction)
        self.row.data['attrs']['project'] = fraction
        self.row.data['attrs']['search'] = fraction


# MIME
# ----


@logger.init('matched', 'DEBUG')
class ParseMime(base.MatchedPeptideBase):
    '''Processes data from the MIME 1.0 format of Mascot'''

    def __init__(self, row):
        super(ParseMime, self).__init__(row)

        self.mime = mime.MimeParser(row)

    def __call__(self):
        '''On start'''

        self.mime()

        self.setids()
        self.setfileheader()

    #     SETTERS

    def setfileheader(self):
        '''
        Stores the project and search names identically since the
        fraction is missing.
        '''

        fraction = os.path.basename(fraction)
        self.row.data['attrs']['project'] = fraction
        self.row.data['attrs']['search'] = fraction
