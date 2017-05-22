'''
    Resources/Parameters/defaults
    _____________________________

    Default, toggleable configurations for XL Discoverer

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules/submodules
import atexit
import os

from namedlist import namedlist

from PySide import QtCore

from xldlib.general import mapping
from xldlib.resources import paths

# OBJECTS
# -------

MinimumScore = namedlist("MinimumScore", "protein peptide")
MaximumEV = namedlist("MaximumEV", "protein peptide")


# PATHS
# -----
DEFAULT_PATH = os.path.join(paths.DIRS['preferences'], 'defaults.json')


# DATA
# ----

DEFAULTS = mapping.Configurations(DEFAULT_PATH, [
    # SYSTEM
    # ------
    # Updates
    ('updates_enabled', True),
    # debugging logs
    ('send_logs', None),
    # ignore close events confirmation
    ('ignore_running_close', False),
    # Fonts
    ('default_font', 'Sans,9,-1,5,50,0,0,0,0,0'),

    # PATHS
    # -----
    ('input_directory', paths.DIRS['home']),
    ('output_directory', paths.DIRS['home']),

    # MEMORY
    # ------
    # 1 mb chunk size, optimal speed
    ('chunk_size', 1024*1024),
    # Boolean for whether to parallelize suitable tasks, or run within a
    # single thread.
    ('use_multiprocessing', False),
    # Number of core to use with individual processes for bottleneck tasks
    # More means more parallelization, but can lead to competing at the CPU
    # no more than QtCore.QThread.idealThreadCount() recommended
    ('max_multiprocessing', QtCore.QThread.idealThreadCount()),

    # INPUT/OUTPUT
    # ------------
    # Pickling provides substantial I/O benefits over my custom-wrapped
    # JSON-serializer, ~20x faster, however, it is also not secure, meaning
    # malicious code can easily be exploited from pickles from untrustworthy
    # sources.
    ('enable_pickle', False),

    # SEARCHING
    # ---------
    # Default value for the search form in find/replace
    ('search_form', u""),
    # Default value for the replace form in find/replace
    ('replace_form', u""),
    # Searches are case/sensitive (can be toggled to off)
    ('search_case_sensitive', True),
    # Search within the current table selection
    ('search_in_selection', True),

    # SCORING
    # -------
    ('Mascot Score', MinimumScore(1, 1)),
    ('Mascot EV', MaximumEV(1, 1)),

    ('Protein Prospector Score', MinimumScore(1, 1)),
    ('Protein Prospector EV', MaximumEV(1, 1)),

    ('Proteome Discoverer Score', MinimumScore(1, 1)),
    ('Proteome Discoverer EV', MaximumEV(1, 1)),

    # MATCHED DATA
    # ------------
    # Boolean for whether to report modifications positions relative to
    # peptide or protein sequence (False means relative to peptide)
    ('peptide_relative_start', False),

    # RAW DATA
    # --------
    # Boolean for whether to validate the MS precursor in a parent scan
    # Useful for non-sequential acquisition methods, such as on FUSION
    # instruments.
    ('check_precursor', False),
    # Percent of product scans without matched precursor scans to
    # then report the files are mismatched
    ('missing_precursor_threshold', 2.0),
    # Value for the maximum number of scan steps to try to find the precursor
    ('precursor_scan_steps', 20),
    # Value for the maximum number of scan steps to try to find the MS1 scan
    ('ms1_scan_steps', 20),
    # Scan level for the MS1 scans, constant "toggleable"
    ('ms1_scan_level', 1),
    # Technically toggleable settings for the precursor and product scan levels
    ('precursor_scan_level', 2),
    ('product_scan_level', 3),

    # LINK FINDING
    # ------------
    # Whether to cluster sequenced peptides from the same MS3 scan, search
    # one of them and then expand the links to all peptides.
    # Works as long as they have the same crosslinker fragment counts
    ('cluster_product_scans', True),
    # Expand the clustered, ambiguous MS3 scans, {'None', 'Intersting', 'All'}
    ("expand_ambiguous", "Interesting"),
    # Maximum number expanded ambiguous IDs reported at "interesting"
    ("interesting_ambiguous", 5),

    # PROTEINS
    # --------
    # Include all search hits from pepXML, etc., or only to select
    # the top identification. It is highly recommended to use
    # database filtering if `all_search_hits` is set to True.
    ('all_search_hits', False),
    # specifies the key used to derive the `best_hit` for the
    # peptide search hits. If `score` is selected, the maximum
    # peptide score is returned. If `rank` is selected, all items
    # with `rank` == 1 are returned
    ('best_hit_key', "Rank"),

    # ERROR THRESHOLDS
    # ----------------
    # Number of isotopes
    ('isotope_threshold', 4),
    # PPM (10**-6 Relative Mass Units)
    ('ppm_threshold', 20),
    # Daltons
    ('mass_threshold', 4000),
    # Daltons, minimum mass for an unmatched peptide
    ('minimum_peptide_mass', 500),
    # Descriptor for which which linknames to relax charges for
    # Can be 'None', 'Standard', or 'Low Confidence'
    ("relax_charges", "Low Confidence"),

    # REPORTS
    # -------
    # Add isotopic labels to the crosslinker
    ('add_isotopic_labels', True),
    # Labeled name to add if no isotope labels found on a peptide
    ('default_isotopic_label', '14N'),
    # Boolean for whether to write hierarchical modifications or flattened
    # modifications. Hierarchical modifications have not yet been implemented
    ('write_hierarchical_modifications', False),
    # Join modifications occurring at the same position
    ('concatenate_hybrid_modifications', True),

    # MS1 QUANTITATION
    # ----------------
    # ID for the current isotope profile set
    ('current_isotope_profile', 2),
    # Whether to include mixed isotope states, like 14N-15N
    # This should be true where labeled population mixing is expected,
    # but turned off where differential analysis is expected
    # (On for crosslinking after mixing, off for crosslinking before mixing)
    ('include_mixed_populations', True),
    # Settings for whether to include various linktypes for quantitation
    ('quantify_interlink', True),
    ('quantify_intralink', True),
    ('quantify_deadend', True),
    # Boolean for whether to lock the retention times for each
    # transition. Forces off if any deuterium labeling occurs
    # within the isotope profiles.
    ('retentiontime_lock', True),
    # Whether to execute quantitation solely at the charge the peptide
    # was identified at or to expand to minus_charge_range and
    # plus_charge_charge
    ('expand_charges', True),
    # Number of charges to consider below identified charge if expand_charges
    ('minus_charge_range', 1),
    # Number of charges to consider above identified charge if expand_charges
    ('plus_charge_charge', 1),
    # Number of isotopes to extract and use during spectral quantitation
    ('quantitative_isotopes', 3),
    # Number of minutes after the sequenced ID to consider
    # in-window (not noise) for the transitions
    ('plus_time_window', 1.5),
    # Number of minutes before the sequenced ID to consider
    # in-window (not noise) for the transitions
    ('minus_time_window', 1.5),
    # Quantify transitions in all files. Still subject to retention
    # time similarities between files.
    ('quantify_globally', True),
    # Percentage similarity in order to consider the two gradients identical
    # for global quantitation. Need to consider filtering that occurs
    # in the reporting of some data formats, most notably PAVA, which
    # means the start and ends may be significantly clipped
    ('gradient_similarity', 0.9),
    # String for which algorithm to use for XIC Peak picking.
    # Algorithm can be either a fitting or a bounding algorithm, but must
    # return a bounded start and end position for the XIC "peak".
    ('xic_picking', 'ab3d'),
    # 'xic_filtering' can be 'id' (sequenced link only),
    # 'nomixing' (strictly between peptides with the same isotope labels),
    #  or 'all' (all)
    ('xic_filtering', 'id'),
    # How to normalize the XIC ratios, which can be to
    # {"Light", "Medium", "Heavy"} (index placeholders) or to {"Max", "Min"}
    # (builtin placeholders)
    ('xic_normalization', 'Heavy'),
    # Mode to calculate ratios for quantitative comparative
    # and ratiotable reports
    # ['Area', 'Intensity']
    ('ratio_quantitation', 'Area'),
    # Specifies whether to weight values during the ratio calculation
    # for the comparative. Can be weighted or unweighted.
    ('weighted_comparative_ratio', True),

    # NumPy method to resolve two overlapping peaks within the m/z spectra,
    # that is, two peaks that both satisfy the PPM window
    # Currently disabled
#    ('paired_mz_mode', "mean"),
#    ('paired_intensity_mode', "sum"),

    # MS3 QUANTITATION
    # ----------------
    # Whether to use reporter ion quantitation
    ('reporterion_quantitation', False),
    ('reporterion_error', 0.2),
    # Specifies the error mode for the reporter ion error, can be
    # ['PPM', 'Da']
    ('reporterion_error_mode', 'Da'),
    # Current ID selected for the reporter ions
    ('current_reporterions', 1),

    # GRAPHS
    # ------
    # Plot graph widgets with antialiasing or without
    ('use_antialiasing', True),
    # Interval ime (in ms) to update the child attributes (and nodes)
    # Uses a tryLock() with a MUTEX to ignore calls in a non-GUI
    # blocking manner
    ('graph_calculation_timeout', 150),
    # Maximum number of points during plotting -- excessive sharply
    # degrades performance, but too much downsampling lowers signal quality
    ('maximum_plot_points', 200000),


    # TRANSITIONS
    # -----------
    # Minimum XIC fit score for peak selection.
    # The XIC score is a weighted average of the dot product,
    # the relative isotope intensity correlation to a theoretical
    # mass lookup table, and the size of the XIC peak.
    ('xic_score_threshold', 0.7),
    # Boolean for whether to normalize the selected charges to the
    # minimum number selected in all isotopic labels
    ('equal_crosslinks', True),
    # Default sorting for the transitions document upon creation
    # {'RT', 'Peptide', 'Score', 'EV', 'Mod Count'}
    ('transition_sortkey', 'Peptide'),
    # Default sort order, ascending (False) or descending (True)
    ('transition_sort_reverse', False),
    # Boolean for whether to snap the transitions peak patch to the
    # the x value grid upon releasing the patch from a pick event.
    ('patch_to_grid', True),
    # Limit exported transitions to those within a certain relative range
    # from the maximum value
    ('filter_transitions_byintensity', False),
    # Relative range to filter values. Minimum value allowed, if filtering,
    # is max_value / 10**(range)
    ('intensity_filtering_range', 3),
    # Filter exported transitions for those above scoring thresholds
    ('filter_transitions_byscore', False),
    # Minimum peptide score for exportation if using score filtering
    ('transition_score_threshold', 1.),
    # Maximum peptide EV for exportation if using score filtering
    ('transition_ev_threshold', 1.),
    # Minimum peak score for exportation if using score-based filtering
    ('transition_peakscore_threshold', 0.5),

    # FINGERPRINTING
    # --------------
    # Default sorting for the fingerprint document upon creation
    # {'RT', ;'peptide', 'score', 'EV', 'Mod Count'}
    ('fingerprint_sortkey', 'peptide'),
    # Default sort order, ascending (False) or descending (True)
    ('fingerprint_sort_reverse', False),

    # PEPTIDE SEARCH
    # --------------
    # Index to `PEPTIDE_CHARGES` for current charge range during
    # peptide matching.
    ('current_peptide_charges', 11),

    # MOWSE
    # -----
    # Scalar incrementers for the mowse database (in Daltons)
    ('protein_interval', 10000),
    ('peptide_interval', 100),
    # Limits on the minimum and maximum peptide mass (in Daltons)
    ('minimum_peptide_mass', 300),
    ('maximum_peptide_mass', 10000),
    # Maximum length for a single protein identifier
    ('protein_identifier_length', 11),
    # Modification database to use for the mowse database construction
    # {'Protein Prospector', 'Mascot', 'Proteome Discoverer'}
    ('modification_engine', 'Protein Prospector'),
    # Definitions for default constant modifications, providing an indexer
    # to the value within the Modifications dataset
    ('constant_modifications', [31]),
    # Definitions for default variable modifications, excluding crosslinkers,
    # providing an indexer to the value within the Modifications dataset
    ('variable_modifications', [4, 6, 44, 80, 163, 178]),

    # PROTEASES
    # ---------
    # Minimum and maximum peptide search lengths during spectral searches
    ('minimum_peptide_length', 5),
    ('maximum_peptide_length', 50),

    # Minimum and maximum number missed cleavages during database construction
    ('minimum_missed_cleavages', 0),
    ('maximum_missed_cleavages', 4),
    # Definition for the current proteolytic enzyme // ideally should
    # be user configurable
    ('current_enzyme', 'Trypsin'),
    # Sites for non-specific cleavage, can be {'0', 'N', 'C', '1', '2'}
    ('nonspecific_cleavage', '0'),

    # MODIFICATIONS
    # -------------
    # Maximum crosslinker fragments per peptide
    ('maximum_crosslinkers', 4),
    # Maximum modifications (including fragments) per peptide
    ('maximum_modifications', 4),

    # UNIPROT
    # -------
    # Default taxonomy for the uniprot downloader // 9606 is H. sapiens
    ('taxonomy', '9606'),
    # Search filter for the fetched proteome entries
    ('taxonomy_filter', u''),
    # Field upon which to place the search filter
    ('taxonomy_filtermode', 'Protein/Gene Name'),
    # Whether to re.escape the search query // hidden, could support re
    ('escape_taxonomy_filter', True),

    # LOW LEVEL
    # ---------
    ('byte_order', {
        'network': "!",
        'big': ">",
        'little': "<"
    })
])

# REGISTERS
# ---------

atexit.register(DEFAULTS.save)
