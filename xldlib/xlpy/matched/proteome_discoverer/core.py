'''
    XlPy/matched/Proteome_Discoverer/core
    _____________________________________

    Objects which parse different Proteome Discoverer file formats
    and are the engines the process the matched data.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# losd modules
import copy
import os
import xml.sax

import numpy as np
#import pandas as pd

from models import params
from xldlib.definitions import re
from xldlib.utils import logger
from xldlib.resources import chemical_defs

# load objects/functions
from .base import ProteomeDiscovererBase
from .sqlite import MSFParser
from ..core import get_engine
from ..csv_ import CSVUtils
from ..pepxml import PepXmlHandler


class ParsePDSqlite3(ProteomeDiscovererBase):
    '''Processes data from the MSF, an sqlite3 format of Proteome Discoverer'''

    def __init__(self, source):
        super(ParsePDSqlite3, self).__init__(source)

        logger.Logging.info("Initializing ParsePDSqlite3....")

    def run(self):
        '''On start'''

        logger.Logging.info("Parsing Proteome Discoverer MSF files...")

        cls = MSFParser(self)
        cls.run()

        for scan in self.group_hits(cls).values():
            hits = scan.pop('hits', [])
            entries = [[scan, v] for v in hits]
            self.append_values(entries)

        self.store_search()
        self.data.setdefault('rank', [1] * len(self.data['id']))
        self.setids()

    def group_hits(self, cls):
        '''
        Re-groups the class peptides to be organized by scan
        number with each hit rank as a separate entry.
        '''

        grouped = {}
        for peptide_id, spectrum_id in cls.peptide_to_spectrum.items():
            entry = cls.peptides[spectrum_id]
            scan = self.get_scan(grouped, entry)

            hit = entry[peptide_id]
            scan['hits'].append(hit)

        return grouped

    def entries(self, scan):
        '''
        Returns the entries to add to matched data based on search hit
        ranking.
        '''

    @staticmethod
    def get_scan(grouped, entry):
        '''Initializes or returns a given scan setting to add hits'''

        num = entry['num']
        try:
            return grouped[num]
        except KeyError:
            # initialize the holder
            data = {'hits': []}
            for key, value in entry.items():
                if not isinstance(value, dict):
                    data[key] = value
            grouped[num] = data
            return data


class ParsePDCsv(ProteomeDiscovererBase, CSVUtils):
    '''Processes data from the tab-delim text export of Proteome Discoverer'''

    dataframe = None
    template = params.TEMPLATES['mods']
    _mod = r'(?:[{}](\d+)|({})|({}))\((.*)\)'

    def __init__(self, source):
        super(ParsePDCsv, self).__init__(source)

        logger.Logging.info("Initializing ParsePDSqlite3....")

        self.engine = get_engine(self.data)
        residues = ''.join(chemical_defs.AMINOACIDS)
        nterm, cterm = map(self.engine.get, ['nterm', 'cterm'])
        self.mod_parser = re.compile(self._mod.format(residues, nterm, cterm))

    def run(self):
        '''Parses the dataframe and converts to the output data holder'''

        logger.Logging.info("Parsing Proteome Discoverer CSV files...")

        self.dataframe = self.parse_dataframe()
        self.process_data()

        self.store_search()
        self.store_mods()
        self.upper_sequences()
        self.calculate_ppms()
        self.data.setdefault('rank', [1] * len(self.data['id']))
        self.setids()
        # TODO:
        # UGHH this has search ranks....
        # self.

    # ------------------
    #       MAIN
    # ------------------

    def parse_dataframe(self):
        '''Parses the matched into via Pandas to an indexed array'''

        index = self.matched["header"]
        sep = self.matched["sep"]
        dataframe = pd.read_csv(self.fileobj, header=index,
                                sep=sep, engine="c")
        # Empty mods should be str
        dataframe.fillna('', inplace=True)
        self.fileobj.close()

        return dataframe

    def store_mods(self):
        '''
        Processes the Proteome Discoverer mod format:
        :
            # Residue + Position (Mod)
            "M1(Oxida); K7(Alken)""
        '''

        headers = self.matched['query']['mods']
        col = self.find_key(headers)
        column = self.dataframe[col].values[:, 0].astype(str)
        mods = np.char.split(column, ';')

        for mod_list in mods:
            mod = self._process_mod(mod_list)
            self.data['mods'].append(mod)

    # ------------------
    #      UTILS
    # ------------------

    def _process_mod(self, mod_list):
        '''Initializes a template and adds all extracted mods'''

        mod = copy.deepcopy(self.template)

        if any(mod_list):
            # [''] is the other possibility from np.char.split()
            matches = map(self.mod_parser.search, mod_list)
            matches = [self._residue_match(i) for i in matches]
            for name, pos in matches:
                mod['certain'].setdefault(name, [])
                mod['certain'][name].append(pos)

        return mod

    @staticmethod
    def _residue_match(item):
        '''Retuns the first match which coinditionally evals to true'''

        pos = item.group(1) or item.group(2) or item.group(3)
        try:
            pos = int(pos)
        except (TypeError, ValueError):
            # terminal modification, group match 2 or 3
            pass
        return (item.group(4), pos)


class ParsePDPepXML(ProteomeDiscovererBase):
    '''Processes data from the pep.XML format of Mascot'''

    def __init__(self, source):
        super(ParsePDPepXML, self).__init__(source)

        logger.Logging.info("Initializing ParsePDPepXML....")
        # self.matched = self.get_matched("protein_prospector", "5.13.1PepXML")
        # self.scoring = self.matched['scoring']

    def run(self):
        '''On start'''

        logger.Logging.info("Parsing Proteome Discoverer pep.XML files...")

        handler = self.parse_xml()
        self.unique_ids.update(handler.unique_ids)

        self.upper_sequences()
        self.calculate_ppms()
        self.data.setdefault('rank', [1] * len(self.data['id']))
        self.setids()
        self._process_header(handler)

    # ------------------
    #       MAIN
    # ------------------

    def parse_xml(self):
        '''Parses the pepXML document and stores all the data'''

        engine = 'Proteome Discoverer'
        handler = PepXmlHandler(self.data, engine=engine)
        parser = xml.sax.make_parser()
        parser.setContentHandler(handler)
        parser.parse(self.fileobj)
        self.fileobj.close()

        return handler

    # ------------------
    #      CALLED
    # ------------------

    def _process_header(self, handler):
        '''
        Doesn't properly store the processs search name.
        :
            handler -- PepXmlHandler instance
        '''

        self.data['project'] = os.path.basename(handler.engine._fraction)
        self.data['search'] = None

