'''
    Chemical/Building_Blocks/elements
    _________________________________

    Contains all relevant, stable elements in the periodic table,
    with their atomic number, mass and abundance for stable isotopes.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load objects/functions
from namedlist import namedlist


__all__ = [
    'DEUTERIUM',
    'ELEMENTS',
]


# OBJECTS
# -------

Isotope = namedlist("Isotope", "number mass abundance")
Element = namedlist("Element", [
    ('symbol'),
    ('name'),
    ('atomic_number'),
    ('valence', None),
    ('isotopes', None)
])


# DATA
# ----

DEUTERIUM = 2


ELEMENTS = {
    "H": Element('H', 'Hydrogen', 1, valence=1, isotopes={
            # isotope definitions (number, mass, abundance)
            1: Isotope(1, 1.0078250321, 99.9885),
            2: Isotope(2, 2.0141017780, 0.0115)
        }
    ),
    "He": Element('He', 'Helium', 2, valence=0, isotopes={
            3: Isotope(3, 3.016029, 0.00014),
            4: Isotope(4, 4.002603, 100.)
        }
    ),
    "Li": Element('Li', 'Lithium', 3, valence=1, isotopes={
            6: Isotope(6, 6.015123, 7.42),
            7: Isotope(7, 7.016005, 92.58)
        }
    ),
    "Be": Element('Be', 'Lithium', 4, valence=2, isotopes={
            9: Isotope(9, 9.012183, 100.)
        }
    ),
    "B": Element('B', 'Boron', 5, valence=3, isotopes={
            10: Isotope(10, 10.012938, 19.8),
            11: Isotope(11, 11.009305, 80.2)
        }
    ),
    "C": Element('C', 'Carbon', 6, valence=4, isotopes={
            12: Isotope(12, 12.0000000, 98.93),
            13: Isotope(13, 13.0033548378, 1.07)
        }
    ),
    "N": Element('N', 'Nitrogen', 7, valence=3, isotopes={
            14: Isotope(14, 14.0030740052, 99.632),
            15: Isotope(15, 15.0001088984, 0.368)
        }
    ),
    "O": Element('O', 'Oxygen', 8, valence=2, isotopes={
            16: Isotope(16, 15.99491463, 99.757),
            17: Isotope(17, 16.9991312, 0.038),
            18: Isotope(18, 17.9991603, 0.205)
        }
    ),
    "F": Element('F', 'Fluorine', 9, valence=1, isotopes={
            19: Isotope(19, 18.998403, 100.00)
        }
    ),
    "Ne": Element('Ne', 'Neon', 10, valence=0, isotopes={
            20: Isotope(20, 19.992439, 90.6),
            21: Isotope(21, 20.993845, 0.26),
            22: Isotope(22, 21.991384, 9.2)
        }
    ),
    "Na": Element('Na', 'Sodium', 11, valence=1, isotopes={
            23: Isotope(23, 22.989770, 100.00)
        }
    ),
    "Mg": Element('Mg', 'Magnesium', 12, valence=2, isotopes={
            24: Isotope(24, 23.985045, 78.90),
            25: Isotope(25, 24.985839, 10.00),
            26: Isotope(26, 25.982595, 11.10)
        }
    ),
    "Al": Element('Al', 'Aluminium', 13, valence=3, isotopes={
            27: Isotope(27, 26.981541, 100.00)
        }
    ),
    "Si": Element('Si', 'Silicon', 14, valence=4, isotopes={
            28: Isotope(28, 27.976928, 92.23),
            29: Isotope(29, 28.976496, 4.67),
            30: Isotope(30, 29.973772, 3.10)
        }
    ),
    "P": Element('P', 'Phosphorus', 15, valence=3, isotopes={
            31: Isotope(31, 30.973763, 100.00)
        }
    ),
    "S": Element('S', 'Sulfur', 16, valence=2, isotopes={
            32: Isotope(32, 31.97207070, 94.93),
            33: Isotope(33, 32.97145843, 0.76),
            34: Isotope(34, 33.96786665, 4.29),
            36: Isotope(36, 35.96708062, 0.02)
        }
    ),
    "Cl": Element('Cl', 'Chlorine', 17, valence=1, isotopes={
            35: Isotope(35, 34.968853, 75.77),
            37: Isotope(37, 36.965903, 24.23)
        }
    ),
    "Ar": Element('Ar', 'Argon', 18, valence=0, isotopes={
            36: Isotope(36, 35.967546, 0.34),
            38: Isotope(38, 37.962732, 0.063),
            40: Isotope(40, 39.962383, 99.6)
        }
    ),
    "K": Element('K', 'Potassium', 19, valence=1, isotopes={
            39: Isotope(39, 38.963708, 93.20),
            40: Isotope(40, 39.963999, 0.012),
            41: Isotope(41, 40.961825, 6.73)
        }
    ),
    "Ca": Element('Ca', 'Calcium', 20, valence=2, isotopes={
            40: Isotope(40, 39.962591, 96.95),
            42: Isotope(42, 41.958622, 0.65),
            43: Isotope(43, 42.958770, 0.14),
            44: Isotope(44, 43.955485, 2.086),
            46: Isotope(46, 45.953689, 0.004),
            48: Isotope(48, 47.952532, 0.19)
        }
    ),
    "Sc": Element('Sc', 'Scandium', 21, valence=3, isotopes={
            45: Isotope(45, 44.955914, 100.)
        }
    ),
    "Ti": Element('Ti', 'Titanium', 22, valence=4, isotopes={
            46: Isotope(46, 45.952633, 8.),
            47: Isotope(47, 46.951765, 7.3),
            48: Isotope(48, 47.947947, 73.8),
            49: Isotope(49, 48.947871, 5.5),
            50: Isotope(50, 49.944786, 5.4)
        }
    ),
    "V": Element('V', 'Vanadium', 23, valence=5, isotopes={
            50: Isotope(50, 49.947161, 0.25),
            51: Isotope(51, 50.943963, 99.75)
        }
    ),
    "Cr": Element('Cr', 'Chromium', 24, valence=3, isotopes={
            50: Isotope(50, 49.946046, 4.35),
            52: Isotope(52, 51.940510, 83.79),
            53: Isotope(53, 52.940651, 9.5),
            54: Isotope(54, 53.938882, 2.36)
        }
    ),
    "Mn": Element('Mn', 'Manganese', 25, valence=2, isotopes={
            55: Isotope(55, 54.938046, 100.00)
        }
    ),
    "Fe": Element('Fe', 'Iron', 26, valence=2, isotopes={
            54: Isotope(54, 53.939612, 5.80),
            56: Isotope(56, 55.934939, 91.72),
            57: Isotope(57, 56.935396, 2.20),
            58: Isotope(58, 57.933278, 0.28)
        }
    ),
    "Co": Element('Co', 'Cobalt', 27, valence=2, isotopes={
            59: Isotope(59, 58.933198, 100.00)
        }
    ),
    "Ni": Element('Ni', 'Nickel', 28, valence=2, isotopes={
            58: Isotope(58, 57.935347, 68.27),
            60: Isotope(60, 59.930789, 26.10),
            61: Isotope(61, 60.931059, 1.13),
            62: Isotope(62, 61.928346, 3.59),
            64: Isotope(64, 63.927968, 0.91)
        }
    ),
    "Cu": Element('Cu', 'Copper', 29, valence=1, isotopes={
            63: Isotope(63, 62.929599, 69.17),
            65: Isotope(65, 64.927792, 30.83)
        }
    ),
    "Zn": Element('Zn', 'Zinc', 30, valence=2, isotopes={
            64: Isotope(64, 63.929145, 48.60),
            66: Isotope(66, 65.926035, 27.90),
            67: Isotope(67, 66.927129, 4.10),
            68: Isotope(68, 67.924846, 18.80),
            70: Isotope(70, 69.925325, 0.60)
        }
    ),
    "Ga": Element('Ga', 'Gallium', 31, valence=3, isotopes={
            69: Isotope(69, 68.925581, 60.1),
            71: Isotope(71, 70.924701, 39.9)
        }
    ),
    "Ge": Element('Ge', 'Germanium', 32, valence=4, isotopes={
            70: Isotope(70, 69.924250, 20.5),
            72: Isotope(72, 71.922080, 27.4),
            73: Isotope(73, 72.923464, 7.8),
            74: Isotope(74, 73.921179, 36.5),
            76: Isotope(76, 75.921403, 7.8),
        }
    ),
    "As": Element('As', 'Arsenic', 33, valence=3, isotopes={
            75: Isotope(75, 74.921596, 100.)
        }
    ),
    "Se": Element('Se', 'Selenium', 34, valence=2, isotopes={
            # 74: Isotope(74, 73.922477, 0.9),
            # 76: Isotope(75.919207, 9.),
            # 77: Isotope(76.919908, 7.6),
            # 78: Isotope(78, 77.917304, 23.5),
            # Treat 80 as monoisotopic
            80: Isotope(80, 79.916521, 49.6),
            # 82: Isotope(82, 81.916709, 9.4),
        }
    ),
    "Br": Element('Br', 'Bromine', 35, valence=1, isotopes={
            79: Isotope(79, 78.918336, 50.69),
            81: Isotope(81, 80.916290, 49.31)
        }
    ),
    "Kr": Element('Kr', 'Krypton', 36, valence=0, isotopes={
            78: Isotope(78, 77.920397, 0.35),
            80: Isotope(80, 79.916375, 2.25),
            82: Isotope(82, 81.913483, 11.6),
            83: Isotope(83, 82.914134, 11.5),
            84: Isotope(84, 83.911506, 57.),
            86: Isotope(86, 85.910614, 17.3)
        }
    ),
    "Rb": Element('Rb', 'Rubidium', 37, valence=1, isotopes={
            85: Isotope(85, 84.911800, 72.17),
            87: Isotope(87, 86.909184, 27.84)
        }
    ),
    "Sr": Element('Sr', 'Strontium', 38, valence=2, isotopes={
            84: Isotope(84, 83.913428, 0.56),
            86: Isotope(86, 85.909273, 9.86),
            87: Isotope(87, 86.908902, 7.0),
            88: Isotope(88, 87.905625, 82.58)
        }
    ),
    "Y": Element('Y', 'Yttrium', 39, valence=3, isotopes={
            89: Isotope(89, 88.905856, 100.)
        }
    ),
    "Zr": Element('Zr', 'Zirconium', 40, valence=4, isotopes={
            90: Isotope(90, 89.904708, 51.45),
            91: Isotope(91, 90.905644, 11.27),
            92: Isotope(92, 91.905039, 17.17),
            94: Isotope(94, 93.906319, 17.33),
            96: Isotope(96, 95.908272, 2.78)
        }
    ),
    "Nb": Element('Nb', 'Niobium', 41, valence=5, isotopes={
            93: Isotope(93, 92.906378, 100.0)
        }
    ),
    "Mo": Element('Mo', 'Molybdenum', 42, valence=6, isotopes={
            92: Isotope(92, 91.906809, 14.84),
            94: Isotope(94, 93.905086, 9.25),
            95: Isotope(95, 94.905838, 15.92),
            96: Isotope(96, 95.904676, 16.68),
            97: Isotope(97, 96.906018, 9.55),
            98: Isotope(98, 97.905405, 24.13),
            100: Isotope(100, 99.907473, 9.63)
        }
    ),
    "Ru": Element('Ru', 'Ruthenium', 44, valence=3, isotopes={
            96: Isotope(96, 95.907596, 5.52),
            98: Isotope(98, 97.905287, 1.88),
            99: Isotope(99, 98.905937, 12.7),
            100: Isotope(100, 99.904218, 12.6),
            101: Isotope(101, 100.905581, 17.0),
            102: Isotope(102, 101.90434, 31.6),
            104: Isotope(104, 103.905422, 18.7),
        }
    ),
    "Rh": Element('Rh', 'Rhodium', 45, valence=3, isotopes={
            103: Isotope(103, 102.905503, 100.0)
        }
    ),
    "Pd": Element('Pd', 'Palladium', 46, valence=2, isotopes={
            102: Isotope(102, 101.905609, 1.02),
            104: Isotope(104, 103.904026, 11.14),
            105: Isotope(105, 104.905075, 22.33),
            106: Isotope(106, 105.903475, 27.33),
            108: Isotope(108, 107.903894, 26.46),
            110: Isotope(110, 109.905169, 11.72)
        }
    ),
    "Ag": Element('Ag', 'Silver', 47, valence=1, isotopes={
            107: Isotope(107, 106.905095, 51.84),
            109: Isotope(109, 108.904754, 48.16)
        }
    ),
    "Cd": Element('Cd', 'Cadmium', 48, valence=2, isotopes={
            106: Isotope(106, 105.906461, 1.25),
            108: Isotope(108, 107.904186, 0.89),
            110: Isotope(110, 109.903007, 12.49),
            111: Isotope(111, 110.904182, 12.8),
            112: Isotope(112, 111.902761, 24.13),
            113: Isotope(113, 112.904401, 12.22),
            114: Isotope(114, 113.903361, 28.73),
            116: Isotope(116, 115.904758, 7.49)
        }
    ),
    "In": Element('In', 'Indium', 49, valence=3, isotopes={
            113: Isotope(113, 112.904056, 4.3),
            115: Isotope(115, 114.903875, 95.7)
        }
    ),
    "Sn": Element('Sn', 'Tin', 50, valence=4, isotopes={
            112: Isotope(112, 111.904826, 0.97),
            114: Isotope(114, 113.902784, 0.65),
            115: Isotope(115, 114.903348, 0.36),
            116: Isotope(116, 115.901744, 14.7),
            117: Isotope(117, 116.902954, 7.7),
            118: Isotope(118, 117.901607, 24.3),
            119: Isotope(119, 118.90331, 8.6),
            120: Isotope(120, 119.902199, 32.4),
            122: Isotope(122, 121.90344, 4.6),
            124: Isotope(124, 123.905271, 5.6)
        }
    ),
    "Sb": Element('Sb', 'Antimony', 51, valence=5, isotopes={
            121: Isotope(121, 120.903824, 57.3),
            123: Isotope(123, 122.904222, 42.7)
        }
    ),
    "Te": Element('Te', 'Tellurium', 52, valence=2, isotopes={
            120: Isotope(120, 119.904021, 0.096),
            122: Isotope(122, 121.903055, 2.6),
            123: Isotope(123, 122.904278, 0.91),
            124: Isotope(124, 123.902825, 4.82),
            125: Isotope(125, 124.904435, 7.14),
            126: Isotope(126, 125.90331, 18.95),
            128: Isotope(128, 127.904464, 31.69),
            130: Isotope(130, 129.906229, 33.8),
        }
    ),
    "I": Element('I', 'Iodine', 53, valence=1, isotopes={
            127: Isotope(127, 126.904477, 100.0)
        }
    ),
    "Xe": Element('Xe', 'Xenon', 54, valence=0, isotopes={
            124: Isotope(124, 123.905894, 0.1),
            126: Isotope(126, 125.904281, 0.09),
            128: Isotope(128, 127.903531, 1.91),
            129: Isotope(129, 128.90478, 26.4),
            130: Isotope(130, 129.90351, 4.1),
            131: Isotope(131, 130.905076, 21.2),
            132: Isotope(132, 131.904148, 26.9),
            134: Isotope(134, 133.905395, 10.4),
            136: Isotope(136, 135.907219, 8.9)
        }
    ),
    "Cs": Element('Cs', 'Cesium', 55, valence=1, isotopes={
            133: Isotope(133, 132.905433, 100.0)
        }
    ),
    "Ba": Element('Ba', 'Barium', 56, valence=2, isotopes={
            130: Isotope(130, 129.906277, 0.11),
            132: Isotope(132, 131.905042, 0.1),
            134: Isotope(134, 133.90449, 2.42),
            135: Isotope(135, 134.905668, 6.59),
            136: Isotope(136, 135.904556, 7.85),
            137: Isotope(137, 136.905816, 11.23),
            138: Isotope(138, 137.905236, 71.7)
        }
    ),
    "La": Element('La', 'Lanthanum', 57, valence=3, isotopes={
            138: Isotope(138, 137.907114, 0.09),
            139: Isotope(139, 138.906355, 99.91)
        }
    ),
    "Ce": Element('Ce', 'Cerium', 58, valence=4, isotopes={
            136: Isotope(136, 135.90714, 0.19),
            138: Isotope(138, 137.905996, 0.25),
            140: Isotope(140, 139.905442, 88.48),
            142: Isotope(142, 141.909249, 11.08)
        }
    ),
    "Pr": Element('Pr', 'Praseodymium', 59, valence=3, isotopes={
            141: Isotope(141, 140.907657, 100.0)
        }
    ),
    "Nd": Element('Nd', 'Neodymium', 60, valence=3, isotopes={
            142: Isotope(142, 141.907731, 27.13),
            143: Isotope(143, 142.909823, 12.18),
            144: Isotope(144, 143.910096, 23.8),
            145: Isotope(145, 144.912582, 8.3),
            146: Isotope(146, 145.913126, 17.19),
            148: Isotope(148, 147.916901, 5.76),
            150: Isotope(150, 149.9209, 5.64)
        }
    ),
    "Sm": Element('Sm', 'Samarium', 62, valence=2, isotopes={
            144: Isotope(144, 143.912009, 3.1),
            147: Isotope(147, 146.914907, 15.0),
            148: Isotope(148, 147.914832, 11.3),
            149: Isotope(149, 148.917193, 13.8),
            150: Isotope(150, 149.917285, 7.4),
            152: Isotope(152, 151.919741, 26.7),
            154: Isotope(154, 153.922218, 22.7),
        }
    ),
    "Eu": Element('Eu', 'Europium', 63, valence=2, isotopes={
            151: Isotope(151, 150.91986, 47.8),
            153: Isotope(153, 152.921243, 52.2)
        }
    ),
    "Gd": Element('Gd', 'Gadolinium', 64, valence=3, isotopes={
            152: Isotope(152, 151.919803, 0.2),
            154: Isotope(154, 153.920876, 2.18),
            155: Isotope(155, 154.822629, 14.8),
            156: Isotope(156, 155.92213, 20.47),
            157: Isotope(157, 156.923967, 15.65),
            158: Isotope(158, 157.924111, 24.84),
            160: Isotope(160, 159.927061, 21.86)
        }
    ),
    "Tb": Element('Tb', 'Terbium', 65, valence=3, isotopes={
            159: Isotope(159, 158.92535, 100.0)
        }
    ),
    "Dy": Element('Dy', 'Dysprosium', 66, valence=3, isotopes={
            156: Isotope(156, 155.924287, 0.06),
            158: Isotope(158, 157.924412, 0.1),
            160: Isotope(160, 159.925203, 2.34),
            161: Isotope(161, 160.926939, 18.9),
            162: Isotope(162, 161.926805, 25.5),
            163: Isotope(163, 162.928737, 24.9),
            164: Isotope(164, 163.929183, 28.2)
        }
    ),
    "Ho": Element('Ho', 'Holmium', 67, valence=3, isotopes={
            165: Isotope(165, 164.930332, 100.0)
        }
    ),
    "Er": Element('Er', 'Erbium', 68, valence=3, isotopes={
            162: Isotope(162, 161.928787, 0.14),
            164: Isotope(164, 163.929211, 1.61),
            166: Isotope(166, 165.930305, 33.6),
            167: Isotope(167, 166.932061, 22.95),
            168: Isotope(168, 167.932383, 26.8),
            170: Isotope(170, 169.935476, 14.9),
        }
    ),
    "Tm": Element('Tm', 'Thulium', 69, valence=3, isotopes={
            169: Isotope(169, 168.934225, 100.0)
        }
    ),
    "Yb": Element('Yb', 'Ytterbium', 70, valence=2, isotopes={
            168: Isotope(168, 167.933908, 0.13),
            170: Isotope(170, 169.934774, 3.05),
            171: Isotope(171, 170.936338, 14.3),
            172: Isotope(172, 171.936393, 21.9),
            173: Isotope(173, 172.938222, 16.12),
            174: Isotope(174, 173.938873, 31.8),
            176: Isotope(176, 175.942576, 12.7)
        }
    ),
    "Lu": Element('Lu', 'Lutetium', 71, valence=3, isotopes={
            175: Isotope(175, 174.940785, 97.4),
            176: Isotope(176, 175.942694, 2.6)
        }
    ),
    "Hf": Element('Hf', 'Hafnium', 72, valence=4, isotopes={
            174: Isotope(174, 173.940065, 0.16),
            176: Isotope(176, 175.94142, 5.2),
            177: Isotope(177, 176.943233, 18.6),
            178: Isotope(178, 177.94371, 27.1),
            179: Isotope(179, 178.945827, 13.74),
            180: Isotope(180, 179.946561, 35.2)
        }
    ),
    "Ta": Element('Ta', 'Tantalum', 73, valence=5, isotopes={
            180: Isotope(180, 179.947489, 0.012),
            181: Isotope(181, 180.948014, 99.99)
        }
    ),
    "W": Element('W', 'Tungsten', 74, valence=6, isotopes={
            180: Isotope(180, 179.946727, 0.13),
            182: Isotope(182, 181.948225, 26.3),
            183: Isotope(183, 182.950245, 14.3),
            184: Isotope(184, 183.950953, 30.67),
            186: Isotope(186, 185.954377, 28.6)
        }
    ),
    "Re": Element('Re', 'Rhenium', 75, valence=4, isotopes={
            185: Isotope(185, 184.952977, 37.4),
            187: Isotope(187, 186.955765, 62.6)
        }
    ),
    "Os": Element('Os', 'Osmium', 76, valence=3, isotopes={
            184: Isotope(184, 183.952514, 0.02),
            186: Isotope(186, 185.953852, 1.58),
            187: Isotope(187, 186.955762, 1.6),
            188: Isotope(188, 187.95585, 13.3),
            189: Isotope(189, 188.958156, 16.1),
            190: Isotope(190, 189.958455, 26.4),
            192: Isotope(192, 191.961487, 41.0)
        }
    ),
    "Ir": Element('Ir', 'Iridium', 77, valence=3, isotopes={
            191: Isotope(191, 190.960603, 37.3),
            193: Isotope(193, 192.962942, 62.7)
        }
    ),
    "Pt": Element('Pt', 'Platinum', 78, valence=2, isotopes={
            190: Isotope(190, 189.959937, 0.01),
            192: Isotope(192, 191.961049, 0.79),
            194: Isotope(194, 193.962679, 32.9),
            195: Isotope(195, 194.964785, 33.8),
            196: Isotope(196, 195.964947, 25.3),
            198: Isotope(198, 197.967879, 7.2)
        }
    ),
    "Au": Element('Au', 'Gold', 79, valence=1, isotopes={
            197: Isotope(197, 196.96656, 100.0)
        }
    ),
    "Hg": Element('Hg', 'Mercury', 80, valence=2, isotopes={
            196: Isotope(196, 195.965812, 0.15),
            198: Isotope(198, 197.96676, 10.1),
            199: Isotope(199, 198.968269, 17.0),
            200: Isotope(200, 199.968316, 23.1),
            201: Isotope(201, 200.970293, 13.2),
            202: Isotope(202, 201.970632, 29.65),
            204: Isotope(204, 203.973481, 6.8)
        }
    ),
    "Tl": Element('Tl', 'Thallium', 81, valence=3, isotopes={
            203: Isotope(203, 202.972336, 29.52),
            205: Isotope(205, 204.97441, 70.48),
        }
    ),
    "Pb": Element('Pb', 'Lead', 82, valence=4, isotopes={
            204: Isotope(204, 203.973037, 1.4),
            206: Isotope(206, 205.974455, 24.1),
            207: Isotope(207, 206.975885, 22.1),
            208: Isotope(208, 207.976641, 52.4)
        }
    ),
    "Bi": Element('Bi', 'Bismuth', 83, valence=5, isotopes={
            209: Isotope(209, 208.980388, 100.0)
        }
    ),
    "Th": Element('Th', 'Thorium', 90, valence=4, isotopes={
            232: Isotope(232, 232.038054, 100.0)
        }
    ),
    "U": Element('U', 'Uranium', 92, valence=3, isotopes={
            234: Isotope(234, 234.040947, 0.006),
            235: Isotope(235, 235.043925, 0.72),
            238: Isotope(238, 238.050786, 99.27)
        }
    )
}
