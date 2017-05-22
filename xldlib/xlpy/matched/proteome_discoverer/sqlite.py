'''
    XlPy/matched/Proteome_Discoverer/sqlite
    _______________________________________

    Implementation-specific parser for Proteome Discoverer MSF files,
    which is an SQLite3 file format.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
from __future__ import division, print_function

import copy
import sqlite3
import sys

from models import params
from xldlib import exception
from xldlib.definitions import re
from xldlib.general import mapping
from xldlib import chemical

# load objects/functions
from .base import ProteomeDiscovererUtils
from .mods import MONOMERS, TERMINAL_MODS
from ..core import get_engine


class SQLiteUtils(ProteomeDiscovererUtils):
    '''Base class to provide shared methods for all SQLite queries'''

    def fetch(self, method, column, table):
        '''
        Fetches a given column or columns from the defined table
        :
            self.fetch("fetchall", "*", "AminoAcidModificationsAminoAcids")
        '''

        self.cursor.execute("SELECT {} FROM {};".format(column, table))

        return getattr(self.cursor, method)()


class ProteomeDiscovererMods(mapping.MethodlessCopyDict, SQLiteUtils):
    '''
    Processes the SQLITE3 mod objects to produce a mod dictionary
    :
        3 SQLITE3 tables -> {modname: formula: res_csv}
    '''

    _attrs = {
        'identifiers': ("AminoAcidModificationID, AminoAcidID",
                        "AminoAcidModificationsAminoAcids"),
        'mods': ("AminoAcidModificationID, ModificationName, "
                 "Abbreviation, Substitution, LeavingGroup",
                 "AminoAcidModifications"),
        'aminoacids': ("AminoAcidID, AminoAcidName, OneLetterCode",
                       "AminoAcids"),
    }
    formula = re.compile(r'\(|\)')

    def __init__(self, cursor, engine):
        super(ProteomeDiscovererMods, self).__init__()

        self.cursor = cursor
        self.engine = engine
        self._terms = {self.engine['nterm'], self.engine['cterm']}

        for attr, (column, table) in self._attrs.items():
            setattr(self, attr, self.fetch("fetchall", column, table))

        self.aminoacids = {i[0] : i[1:] for i in self.aminoacids}
        self.mods = {i[0] : i[1:] for i in self.mods}

        self.ids = {}

        self.add_standard()
        self.add_terminal()
        self.process_residues()

    # ------------------
    #       MAIN
    # ------------------

    def add_standard(self):
        '''Adds the standard mods which do not have a "terminal" ID'''

        for mod_id, aminoacid_id in self.identifiers:
            modname, abbrev, string_formula, leaving_group = self.mods[mod_id]
            if 'Mascot' in modname:
                continue

            self.ids[mod_id] = modname
            formula = self._get_formula(string_formula, modname, leaving_group)
            if formula is None:
                continue
            holder = [formula, set()]
            self.setdefault(modname, holder)
            self.setdefault(abbrev, holder)

            residue = self._get_residue(aminoacid_id)
            self[modname][1].add(residue)

    def add_terminal(self):
        '''Adds the mods which are terminal only'''

        standard_ids = set(i[0] for i in self.identifiers)
        terminal_ids = set(self.mods).difference(standard_ids)
        for mod_id in terminal_ids:
            modname, abbrev = self.mods[mod_id][0:2]
            self.ids[mod_id] = modname

            self.setdefault(modname, TERMINAL_MODS[modname])
            self.setdefault(abbrev, TERMINAL_MODS[modname])

    def process_residues(self):
        '''Processes the residues from a set to the CSV format'''

        # memoize to avoid double processing the same holder from the
        # modname and the abbrev
        memo = set()
        for values in self.values():
            id_ = id(values)

            if id_ not in memo:
                residues = ','.join(sorted(values[1]))
                values[1] = residues
                memo.add(id_)

    # ------------------
    #      UTILS
    # ------------------

    def _get_formula(self, string_formula, modname, leaving_group):
        '''
        Produces the net mod formula, with the addition or overall formula
        defined by string_formula and the loss by the leaving_group.
        If no formula is defined or is a monomer formula (not chemical),
        an AssertionError or AttributeError is defined and the formula
        is attempted to be solved via .mods.MONOMERS.
        '''

        try:
            assert string_formula
            string_formula = self.formula.sub('', string_formula)
            formula = chemical.Molecule(string_formula)
            formula.update_formula(leaving_group, count=-1)
            formula = formula.tostr()

        except (AssertionError, AttributeError):
            formula = MONOMERS.get(modname)
            if formula is None:
                print(exception.CODES['024'].format(modname), file=sys.stderr)
        return formula

    def _get_residue(self, aminoacid_id):
        '''Returns the residue name based on whether N-/C-term or internal'''

        aminoacid_name, one_letter = self.aminoacids[aminoacid_id]

        if aminoacid_name in self._terms:
            residue = aminoacid_name
        else:
            residue = one_letter

        return residue


class MSFParser(SQLiteUtils):
    '''
    Provides convenient methods to parse the MSF file format, which is
    a simple, readable SQLITE3 format.
    '''

    _fraction = None
    _path_sep = re.compile(r'\\|/')

    def __init__(self, parent):
        super(MSFParser, self).__init__()

        self.data = parent.data
        self.engine = get_engine(self.data)
        self.source = parent.source
        self.fragments = parent.fragments

        self.database = sqlite3.connect(parent.fileobj.name)
        self.cursor = self.database.cursor()

        self.peptide_to_spectrum = {}
        self.peptides = mapping.OrderedRecursiveDict()
        self.proteins = {}

        # all mods are defined internally within the file
        mods = ProteomeDiscovererMods(self.cursor, self.engine)
        # need to convert to the namedtuple format
        params.tupleize(mods)
        self.mod_ids = mods.ids
        self.engine['mods'].update(mods)

    def run(self):
        '''On start'''

        self.init_spectrum()

        self.fetch_enzyme()
        self.set_file()
        self.add_spectrum()
        self.add_scores()
        self.add_mods()
        self.add_ppms()
        self.set_proteins()
        self.add_proteins()

    # ------------------
    #       MAIN
    # ------------------

    def init_spectrum(self):
        '''Sets the peptides with a SpectrumID as a key reference'''

        columns = "PeptideID, SpectrumID, Sequence, SearchEngineRank"
        self.cursor.execute("SELECT {} FROM Peptides;".format(columns))
        # Spectrum ID is the unique spectral identifier
        # Peptide ID is the unique peptide identifier
        # Sequence is the peptide sequence, ex: "KATNE"
        for peptide_id, spectrum_id, sequence, rank in self.cursor:
            self.peptide_to_spectrum[peptide_id] = spectrum_id
            entry = self.peptides[spectrum_id][peptide_id]
            entry['peptide'] = sequence
            entry['rank'] = rank

    def fetch_enzyme(self):
        '''Extracts the proteolytic enzyme for the peptide search'''

        columns = "ParameterName, ParameterValue"
        table = "ProcessingNodeParameters"
        items = {k: v for k, v in self.fetch("fetchall", columns, table)}
        try:
            self.data['enzyme'] = items['Enzyme']
        except KeyError:
            # no enzyme defined
            pass

    def set_file(self):
        '''Sets the current file name uses from the RAW file'''

        files = self.fetch("fetchall", "FileName", "FileInfos")
        # joins consecutive file names together, FileInfos should be 1
        # use regex path splitter, since Windows path mappings don't work
        # on Linux or OS X.
        files = (self._path_sep.split(i[0])[-1] for i in files)
        self._fraction = ' - '.join(files)

        for entry in self.peptides.values():
            entry['fraction'] = self._fraction

    def add_spectrum(self):
        '''Adds the spectral data, which includes the m/zs and charge states'''

        columns = "SpectrumID, ScanNumbers, Charge, Mass"
        self.cursor.execute("SELECT {} FROM SpectrumHeaders;".format(columns))
        # Spectrum ID is the unique spectral identifier
        # num is the scan number associated with the spectral ID
        # charge is the charge state of the peptide
        # mass is the singly-charged mass of the peptide
        for spectrum_id, num, charge, mass in self.cursor:
            # peptide_ids = self.spectrum[spectrum_id]

            self.peptides[spectrum_id]['num'] = num
            self.peptides[spectrum_id]['z'] = charge
            # mz = masstools.mz(mass - params.PROTON_MASS, charge, 0)
            self.peptides[spectrum_id]['m/z'] = mz

    def add_scores(self):
        '''
        Adds the score and calculates the EV from the score
        :
            score == -10*log(ev, 10)
        '''

        columns = "PeptideID, ScoreValue"
        self.cursor.execute("SELECT {} FROM PeptideScores;".format(columns))
        # Peptide ID is the unique peptide identifier, which
        # is for each peptide hit from the spectral ID
        # Score is the - 10 * log(p-value, 10)
        for peptide_id, score in self.cursor:
            expect = 10 ** (-score / 10)
            spectrum_id = self.peptide_to_spectrum[peptide_id]

            entry = self.peptides[spectrum_id][peptide_id]
            entry['score'] = score
            # need to calculate the p-value, or expectation value
            entry['ev'] = expect

    def add_mods(self):
        '''Finds all the target mods from the IDs and adds them to a holder'''

        self._mod_templates()
        self._internal_mods()
        self._terminal_mods()

    def add_ppms(self):
        '''Calculates the PPMs from the mods and peptides for each entry'''

        keys = ['peptide', 'm/z', 'z']
        for peptide_id, spectrum_id in self.peptide_to_spectrum.items():
            entry = self.peptides[spectrum_id]
            hit = entry[peptide_id]
            mod = hit['mods']
            peptide, exper, charge = map(entry.get, keys)

            hit['formula'] = formula = self.calculate_formula(peptide, mod)
            hit['ppm'] = self.calculate_ppm(formula, mod, exper, charge)

    def set_proteins(self):
        '''Creates a {ProteinID: (UniProt ID: Protein Name)} holder'''

        columns = 'ProteinID, Description'
        table = "ProteinAnnotations"
        self.cursor.execute("SELECT {0} FROM {1};".format(columns, table))

        for protein_id, description in self.cursor:
            # description == '>sp|P62894|CYC_BOVIN Cytochrome ...'
            id_, name = description.split('|')[1:]
            self.proteins[protein_id] = (id_, name)

    def add_proteins(self):
        '''Adds the protein names and IDs to each entry'''

        columns = "PeptideID, ProteinID"
        self.cursor.execute("SELECT {} FROM PeptidesProteins;".format(columns))

        for peptide_id, protein_id in self.cursor:
            spectrum_id = self.peptide_to_spectrum[peptide_id]
            entry = self.peptides[spectrum_id][peptide_id]
            id_, name = self.proteins[protein_id]

            entry['id'] = id_
            entry['name'] = name

    # ------------------
    #      UTILS
    # ------------------

    #      MODS

    def _internal_mods(self):
        '''Adds all the internal modifications to the mod holders'''

        columns = "PeptideID, AminoAcidModificationID, Position"
        table = "PeptidesAminoAcidModifications"
        self.cursor.execute("SELECT {} FROM {};".format(columns, table))

        for peptide_id, mod_id, position in self.cursor:
            spectrum_id = self.peptide_to_spectrum.get(peptide_id)
            modname = self.mod_ids[mod_id]

            # for some weird reason, the mods can have peptide IDs which don't
            # exist otherwise, causing errors. Not decoys, nothing.
            if spectrum_id is not None:
                mods = self.peptides[spectrum_id][peptide_id]['mods']
                mods['certain'].setdefault(modname, [])
                mods['certain'][modname].append(position)

    def _terminal_mods(self):
        '''Adds all the N-/C-terminal modifications to the mod holders'''

        columns = "PeptideID, TerminalModificationID"
        table = "PeptidesTerminalModifications"
        self.cursor.execute("SELECT {} FROM {};".format(columns, table))
        for peptide_id, mod_id in self.cursor:
            spectrum_id = self.peptide_to_spectrum.get(peptide_id)

            # for some weird reason, the mods can have peptide IDs which don't
            # exist otherwise, causing errors. Not decoys, nothing.
            if spectrum_id is not None:
                mods = self.peptides[spectrum_id][peptide_id]['mods']

                modname = self.mod_ids[mod_id]
                mods['certain'].setdefault(modname, [])
                if self.engine['nterm'] in self.engine['mods'][modname][1]:
                    mods['certain'][modname].append(self.engine['nterm'])

                else:
                    mods['certain'][modname].append(self.engine['cterm'])

    def _mod_templates(self):
        '''Sets the mod template holders for each peptide ID'''

        template = params.TEMPLATES['mods']
        for peptide_id, spectrum_id in self.peptide_to_spectrum.items():
            hit = self.peptides[spectrum_id][peptide_id]
            hit.setdefault('mods', copy.deepcopy(template))
