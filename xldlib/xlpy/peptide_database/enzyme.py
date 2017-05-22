#'''
#    XlPy/Peptide_Database/enzyme
#    ____________________________
#
#    Predicts the theoretical cut sites for each target protein sequence.
#
#    :copyright: (c) 2015 The Regents of the University of California.
#    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
#'''
#
## load modules
#from models import config, params
#from xldlib.definitions import re
#from xldlib.resources import chemical_defs
#
## load objects/functions
#from collections import namedtuple
#
#from .decoy import shuffle_sequence
#
## ------------------
##     CUT SITES
## ------------------
#
# TODO: Depricate
#
#class CutRegex(str):
#    '''Generates a string pattern that can be compiled to a regex'''
#
#    amino_acids = chemical_defs.ONE_LETTER_MIXED
#    cut_re = namedtuple("Cut", "index aa res")
#    _dataset = params.FINGERPRINT_HDF5
#
#    def __new__(cls, enzyme):
#        cls.enzyme = enzyme
#        cls.cut = cls.enzyme['cut']
#        cls.nocut = cls.enzyme['nocut']
#        cls.side = cls.enzyme['side']
#
#        cls.cut_slice = cls.get_cut_slice()
#        cls.res_slice = cls.get_res_slice()
#
#        cls.cut_sites = r''
#        for index, res in enumerate(cls.cut):
#            cls.add_cut(index, res)
#
#        return super(CutRegex, cls).__new__(cls, cls.cut_sites)
#
#    # ------------------
#    #       MAIN
#    # ------------------
#
#    @classmethod
#    def add_cut(cls, index, res):
#        '''Adds a given cut position, removing the nocut sites'''
#
#        amino_acids = cls.remove_nocut(res)
#        data = cls.cut_re(index, amino_acids, res)
#        if cls.side == 'C':
#            cls.cut_sites += cls._cterm_cut_regex(data)
#        else:
#            cls.cut_sites += cls._nterm_cut_regex(data)
#
#    @classmethod
#    def get_cut_slice(cls):
#        '''
#        Grabs the adjustment for the nocut positions based on whether the
#        enzyme is an N- or C-terminal protease, which when used on a nocut
#        will return the cut residue ('K' in 'KP' for C-term).
#        :
#            self._cut_side == 'N' -> cut_slice() -> slice(1, None)
#            self._cut_side == 'C' -> cut_slice() -> slice(0, 1)
#        '''
#
#        assert cls.side in {'N', 'C'}
#        if cls.side == 'C':
#            cut_slice = slice(0, 1)
#        else:
#            cut_slice = slice(1, None)
#
#        return cut_slice
#
#    @classmethod
#    def get_res_slice(cls):
#        '''
#        Grabs the adjustment for the nocut positions based on whether the
#        enzyme is an N- or C-terminal protease, which when used on a nocut
#        will return the flanking residue ('P' in 'KP' for C-term).
#        :
#            self._cut_side == 'N' -> res_slice() -> slice(0, 1)
#            self._cut_side == 'C' -> res_slice() -> slice(1, None)
#        '''
#
#        assert cls.side in {'N', 'C'}
#        if cls.side == 'C':
#            res_slice = slice(1, None)
#        else:
#            res_slice = slice(0, 1)
#
#        return res_slice
#
#    @classmethod
#    def remove_nocut(cls, res):
#        '''Produces all the amino acids with no cut'''
#
#        nocut = set()
#        for item in cls.nocut:
#            if item[cls.cut_slice] == res:
#                nocut.add(item[cls.res_slice])
#
#        return ''.join(i for i in cls.amino_acids if i not in nocut)
#
#    # ------------------
#    #       UTILS
#    # ------------------
#
#    @staticmethod
#    def _cterm_cut_regex(data):
#        '''Adds C-term cut patterns to the regex'''
#
#        if data.index == 0:
#            string = r'{0}[{1}]'
#        else:
#            string = r'|{0}[{1}]'
#
#        string = string.format(data.res, data.aa)
#
#        return string
#
#    @staticmethod
#    def _nterm_cut_regex(data):
#        '''Adds C-term cut patterns to the regex'''
#
#        if data.index == 0:
#            string = r'[{0}]{1}'
#        else:
#            string = r'|[{0}]{1}'
#
#        string = string.format(data.aa, data.res)
#
#        return string
#
#
#class CutUtils(object):
#    '''
#    Provides mehtods to cut target sequences after generating
#    a regex mimicking a proteolytic enzyme
#    '''
#
#    _compress = config.MEMORY['hdf5_data']
#    # objects for making cut sites
#    term = namedtuple("Term", "id missed start end")
#    cut_data = namedtuple("Cut", "seq start nterm cterm")
#    cut_re = namedtuple("Cut", "index aa res")
#
#    amino_acids = chemical_defs.ONE_LETTER_MIXED
#    # temporary data holder for transition
#    _peptides = []
#
#    # ------------------
#    #       PUBLIC
#    # ------------------
#
#    def cut_sequences(self):
#        '''Cuts the target sequences into a series of protelytic peptides'''
#
#        self.init_cuts()
#
#        for id_ in self.sequences:
#            grp = self.grp['base_peptides'][self._mode][str(id_)]
#            base_length = grp.value.size
#
#            for missed in range(self.max_missed):
#                self.join_peptides(id_, base_length, missed)
#
#                self.add_cuts(id_, missed)
#
#    def add_cuts(self, id_, missed):
#        '''Adds the peptide sequences to the HDF5 dataset'''
#
#        key = 'peptides/{}/{}'.format(self._mode, missed)
#        ids = self.grp[key].create_group(str(id_))
#
#        peptide, start = zip(*self._peptides)
#        ids.create_dataset('peptide', data=peptide, dtype=self.peptide_dtype,
#                           **self._compress)
#        ids.create_dataset('start', data=start, **self._compress)
#
#    def init_cuts(self):
#        '''Enacts all the cuts and randomizes each sequences if decoy set on'''
#
#        kwds = self._compress.copy()
#        base = self.grp['base_peptides'].create_group(self._mode)
#        for id_ in self.sequences:
#            sequence = self.sequences[id_].seq
#            if self._mode == 'decoy':
#                sequence = shuffle_sequence(sequence, self.consistent_decoys)
#
#            peptides, maxlen = self.cut_sequence(sequence)
#            kwds['dtype'] = 'S{}'.format(maxlen)
#            base.create_dataset(str(id_), data=peptides, **kwds)
#
#    def cut_sequence(self, sequence):
#        '''Forms the base peptides from the cut sites from the target seq'''
#
#        cut = self.cut_regex()
#        peptides = []
#        maxlen = 0
#
#        while sequence:
#            match = cut.search(sequence)
#
#            if match is None:
#                # end of the sequence, no more cuts
#                seq = sequence.encode('utf-8')
#                sequence = ''
#
#            else:
#                cut_pos = match.start() + 1
#                seq = sequence[:cut_pos].encode('utf-8')
#                sequence = sequence[cut_pos:]
#
#            maxlen = max(maxlen, len(seq))
#            peptides.append(seq)
#
#        return peptides, maxlen
#
#    def join_peptides(self, id_, base_length, missed):
#        '''Joins base peptides and forms protelytic peptides for searches'''
#
#        self._peptides = []
#        # need to offset the index by the missed count
#        for index in range(base_length - missed):
#            end_index = index + missed + 1
#            term = self.term(id_, missed, index, end_index)
#
#            peptide = self._get_peptide(term)
#            start = self._get_start(term)
#            nterm, cterm = self.get_terms(term, peptide)
#
#            # invalid data
#            if nterm < 0 or cterm < 0:
#                continue
#            data = self.cut_data(peptide, start, nterm, cterm)
#
#            method = "nonspecific_{0}term".format(self.nonspecific.lower())
#            getattr(self, method)(data)
#
#    def enzyme(self):
#        '''Grabs the proteolytic enzyme for the cut regexes'''
#
#        if not hasattr(self, "_enzyme"):
#            enzyme = params.MASS_FINGERPRINT['enzyme']
#            current = enzyme['current']
#            self._enzyme = enzyme['options'][current]
#
#        return self._enzyme
#
#    def cut_regex(self):
#        '''Grabs the regex for each peptide'''
#
#        if not hasattr(self, "_cut_regex"):
#            cut_regex = CutRegex(self.enzyme())
#            self._cut_regex = re.compile(cut_regex)
#
#        return self._cut_regex
#
#
#
#class CutSites(CutUtils):
#    '''
#    Base class to return the protelytic peptides with various missed
#    cleavages.
#    '''
#
#    peptide = namedtuple("Peptide", "seq start")
#
#    # ------------------
#    #   PEPTIDE UTILS
#    # ------------------
#
#    def _get_peptide(self, term):
#        '''Returns the peptide from the self.base_peptides slice'''
#
#        seqs = self.grp['base_peptides'][self._mode][term.id].value
#        return ''.join(i.decode('utf-8') for i in seqs[term.start: term.end])
#
#    def _get_start(self, term):
#        '''Returns the peptide start position in the sequence'''
#
#        seqs = self.grp['base_peptides'][self._mode][term.id].value
#        return len(''.join(i.decode('utf-8') for i in seqs[:term.start])) + 1
#
#    # ------------------
#    # NON-SPECIFIC ENDS
#    # ------------------
#
#    def get_terms(self, term, peptide):
#        '''
#        Returns the N- and C-term bounds (None) meaning no bound
#        for the non-specific ends on both sides
#        '''
#
#        if term.missed == 0:
#            # no bounds for previous cut sites
#            nterm = len(peptide) - self.min_length
#            cterm = len(peptide) - self.min_length
#
#        else:
#            # bound by cut up one or two
#            seqs = self.grp['base_peptides'][self._mode][term.id].value
#            nterm = len(seqs[term.start]) - 1
#            cterm = len(seqs[term.end - 1]) - 1
#
#        return nterm, cterm
#
#    def nonspecific_0term(self, data):
#        '''Adds a sequence if there are no non-specific termini'''
#
#        # only consider peptides above min length threshold
#        if self.min_length < len(data.seq) < self.max_length:
#            peptide = self.peptide(data.seq.encode('utf-8'), data.start)
#            self._peptides.append(peptide)
#
#    def nonspecific_1term(self, data):
#        '''Adds a series of sequences with nonspecific cuts on 1 term'''
#
#        self.nonspecific_nterm(data)
#        self.nonspecific_cterm(data)
#
#    def nonspecific_nterm(self, data):
#        '''Adds a series of sequences with nonspecific cuts on the nterm'''
#
#        counter = 0
#        while counter <= data.nterm:
#            seq = data.seq[counter:]
#            start = data.start + counter
#
#            if self.min_length < len(seq) < self.max_length:
#                peptide = self.peptide(seq.encode('utf-8'), start)
#                self._peptides.append(peptide)
#
#            else:
#                break
#
#            counter += 1
#
#    def nonspecific_cterm(self, data):
#        '''Adds a series of sequences with nonspecific cuts on the cterm'''
#
#        counter = 0
#        seq_len = len(data.seq)
#        while counter <= data.cterm:
#            # slowly trim from end
#            seq = data.seq[:seq_len - counter]
#
#            if self.min_length < len(seq) < self.max_length:
#                peptide = self.peptide(seq.encode('utf-8'), data.start)
#                self._peptides.append(peptide)
#            else:
#                break
#
#            counter += 1
#
#    def nonspecific_2term(self, data):
#        '''Adds a series of sequences with nonspecific cuts on both terms'''
#
#        counter = 0
#        while counter <= data.nterm:
#            # slowly trim from end
#            seq = data.seq[counter:]
#            start = data.start + counter
#            tmp_data = self.cut_data(seq, start, data.nterm, data.cterm)
#
#            if self.min_length < len(seq) < self.max_length:
#                self.nonspecific_cterm(tmp_data)
#            else:
#                break
#
#            counter += 1
