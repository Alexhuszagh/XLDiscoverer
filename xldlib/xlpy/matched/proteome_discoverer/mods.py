'''
    XlPy/matched/Proteome_Discoverer/mods
    _____________________________________

    Non-atomic building-block specifications and various N-/C- terminal
    mods via mapping data structures.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

MONOMERS = {
    'Galactosyl': 'H10 C6 O6',
    'Glucosylgalactosyl': 'H20 C12 O11',
    'Hep': 'H12 C7 O6',
    'Hex': 'H10 C6 O5',
    'Hex(1)HexNAc(1)NeuAc(1)': 'H40 C25 N2 O18',
    'Hex(1)HexNAc(1)NeuAc(2)': 'H57 C36 N3 O26',
    'Hex(1)HexNAc(1)dHex(1)': 'H33 C20 N1 O14',
    'Hex(1)HexNAc(2)': 'H36 C22 N2 O15',
    'Hex(1)HexNAc(2)Pent(1)': 'H44 C27 N2 O19',
    'Hex(1)HexNAc(2)dHex(1)': 'H46 C28 N2 O19',
    'Hex(1)HexNAc(2)dHex(1)Pent(1)': 'H54 C33 N2 O23',
    'Hex(1)HexNAc(2)dHex(2)': 'H56 C34 N2 O23',
    'Hex(2)': 'H20 C12 O10',
    'Hex(2)HexNAc(2)': 'H46 C28 N2 O20',
    'Hex(2)HexNAc(2)Pent(1)': 'H54 C33 N2 O24',
    'Hex(2)HexNAc(2)dHex(1)': 'H56 C34 N2 O24',
    'Hex(3)': 'H30 C18 O15',
    'Hex(3)HexNAc(1)Pent(1)': 'H51 C31 N1 O24',
    'Hex(3)HexNAc(2)': 'H56 C34 N2 O25',
    'Hex(3)HexNAc(2)P(1)': 'H56 C34 N2 O25 P',
    'Hex(3)HexNAc(4)': 'H82 C50 N4 O35',
    'Hex(4)HexNAc(4)': 'H92 C56 N4 O40',
    'Hex(5)HexNAc(2)': 'H76 C46 N2 O35',
    'Hex(5)HexNAc(4)': 'H102 C62 N4 O45',
    'Hex1HexNAc1': 'H23 C14 N1 O10',
    'HexNAc': 'H13 C8 N1 O5',
    'HexNAc(1)dHex(1)': 'H23 C14 N1 O9',
    'HexNAc(1)dHex(2)': 'H33 C20 N1 O13',
    'HexNAc(2)': 'H26 C16 N2 O10',
    'HexNAc(2)dHex(1)': 'H36 C22 N2 O14',
    'HexNAc(2)dHex(2)': 'H46 C28 N2 O18',
    'PhosphoHex': 'H11 C6 O8 P1',
    'PhosphoHexNAc': 'H14 C8 N1 O8 P1',
    'dHex': 'H10 C6 O4',
    'dHex(1)Hex(3)HexNAc(4)': 'H92 C56 N4 O39',
    'dHex(1)Hex(4)HexNAc(4)': 'H102 C62 N4 O44',
    'dHex(1)Hex(5)HexNAc(4)': 'H112 C68 N4 O49',
    'Sulfenic-DSSO': 'C3 H4 S1 O2',
    'Thiol-DSSO': 'C3 H2 S1 O1'
}

TERMINAL_MODS = {
    # this is C-terminal, don't ask me why or how
    'N-Acetyl': ['C2 H2 O1', ['C-Terminus']],
    'Pyro-glu': ['H-3 N-1', ['N-Terminus']]
}
