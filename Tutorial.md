# XL Discoverer Tutorial

This tutorial should walk you through the basics to use XL Discoverer through the standard interface.

**Table of Contents**

- [Goals of XL Discoverer](#goals-of-xl-discoverer)
- [XL Discoverer Tools](#xl-discoverer-tools)
- [XL Discoverer Use](#xl-discoverer-use)
  - [Splash Menu](#splash-menu)
  - [Standard Analysis -- Link Discoverer](#standard-analysis----link-discoverer)
    - [Menu Location](#menu-location)
    - [Overview](#overview)
    - [Basic Use](#basic-use)
      - [Link Discoverer -- Input Files](#link-discoverer----input-files)
      - [Link Discoverer -- Select Cross-Linkers](#link-discoverer----select-cross-linkers)
      - [Link Discoverer -- Run](#link-discoverer----run)
  - [ID & Quantitative Analysis -- Quantitative Link Discoverer](#id--quantitative-analysis----quantitative-link-discoverer)
    - [Menu Location](#menu-location-1)
    - [Overview](#overview-1)
    - [Basic Use](#basic-use-1)
  - [Quantitative Analysis -- MS/MS Quantitation](#quantitative-analysis----msms-quantitation)
    - [Menu Location](#menu-location-2)
    - [Overview](#overview-2)
    - [Basic Use](#basic-use-2)
  - [Quantitative Analysis -- Load Transitions](#quantitative-analysis----load-transitions)
    - [Menu Location](#menu-location-3)
    - [Overview](#overview-3)
    - [Basic Use](#basic-use-3)
- [Input File Formats](#input-file-formats)
  - [Input Types](#input-types)
  - [Compressed Files and File Archives](#compressed-files-and-file-archives)
  - [Raw Scan Settings](#raw-scan-settings)
  - [Matched Peptide Output Settings](#matched-peptide-output-settings)
    - [Protein Prospector](#protein-prospector)
      - [Minimal Settings Example](#minimal-settings-example)
      - [Minimal Settings Explanation](#minimal-settings-explanation)
- [Advanced Settings](#advanced-settings)
  - [Adding Custom Mods](#adding-custom-mods)
    - [Adding New Mods](#adding-new-mods)
  - [Cross-Link Error Thresholds](#cross-link-error-thresholds)
    - [Submenu Location](#submenu-location)
  - [Protein Names and Filtering](#protein-names-and-filtering)
    - [Submenu Location](#submenu-location-1)
    - [Name and Filtering Categories](#name-and-filtering-categories)
        - [Greylist](#greylist)
        - [Blacklist](#blacklist)
        - [Common Name](#common-name)
        - [Gene Name](#gene-name)
        - [Limited Database](#limited-database)
        - [Decoy Database](#decoy-database)
    - [Batch Edit Protein Lists](#batch-edit-protein-lists)
    - [Search Hits](#search-hits)
  - [Customize Reports](#customize-reports)
    - [Submenu Location](#submenu-location-2)
  - [Editing Cross-Linkers](#editing-cross-linkers)
    - [Location](#location-1)
    - [Adding/Editing Cross-Linkers](#addingediting-cross-linkers)
    - [Removing Cross-Linkers](#removing-cross-linkers)
  - [Edit Column Order](#edit-column-order)
    - [Location](#location-2)
    - [Editing a Report's Column Order](#editing-a-reports-column-order)
    - [Toggling the Comparative Report](#toggling-the-comparative-report)
- [Report Descriptions](#report-descriptions)
  - [Interlinks](#interlinks)
  - [Quantitative](#quantitative)
  - [Best IDs -- All | File](#transitions)
  - [Comparative](#comparative)
  - [Skyline](#skyline)
  - [Low Confidence](#low-confidence)
  - [Mutlilinks](#mutlilinks)
  - [Singles](#singles)
  - [Deadends](#deadends)
  - [Intralinks](#intralinks)
  - [Interlinks](#interlinks)
  - [Interlinks](#interlinks)
- [Testing](#testing)
  - [Checked Features](#checked-features)
- [Updates](#updates)


## Goals of XL Discoverer

* Automated Crosslinking Mass Spectrometry (XL-MS) data analysis
* Simple, clean GUI (graphical user interface)
* Configurable crosslink discovery and reports
* Automated crosslinked peptide quantitation and robust validation

## XL Discoverer Tools

* Link Discoverer
    * Automated Link Discovery
* Quantitative Link Discoverer
    * Link Discovery and Quantitation
* Mass Fingerprinting
    * Visualization and validation identified cross-linked peptides
* Transitions
    * Quantitative Cross-Linked Peptide Document Editor

## XL Discoverer Use

### Splash Menu

![Image of Splash Menu]
(http://i.imgur.com/OZ5e6S4.png)

### Standard Analysis -- Link Discoverer

#### Menu Location

![Image of Link Discoverer Splash Menu Location]
(http://i.imgur.com/G0uisZT.png)

#### Overview

* Identifies cross-linked peptides that are:
    * Dead-end
    * Intra-links
    * Inter-links with up to n linked-peptides

* Automatically generates configurable reports
    * Comparative reports between samples
    * Best peptide filtering
    * Processed data for exportation to [Skyline](https://brendanx-uw1.gs.washington.edu/labkey/project/home/software/Skyline/begin.view), [xiNet](http://crosslinkviewer.org/), etc.

#### Basic Use

<table>
  <tr>
    <td align="center"><h5>Input Files</h5></td>
    <td align="center"><h5>Select Cross-Linkers</h5></td>
    <td align="center"><h5>Run</h5></td>
  </tr>
  <tr>
    <td><img src="http://i.imgur.com/9huDNkR.png" alt="Input Files"></td>
    <td><img src="http://i.imgur.com/aaTetkV.png" alt="Select Cross-Linkers"></td>
    <td><img src="http://i.imgur.com/nQtX0zY.png" alt="Run"></td>
  </tr>
</table>

##### Link Discoverer -- Input Files

> **How to add files**
> Click a cell, which will create a native file dialog to select an item. Select the spectral or matched peptide file desired, and then input the comparable information for all columns in the row. If you need to activate the file dialog for the current cell, simply press enter or double click the cell.

&nbsp;
> **How to remove files**
> Either click "Clear All", which will remove all files in the table from the analysis, or click a cell and exit out of the file dialog.

See [Input File Formats](#input-file-formats) for more information on the MS scans and MS3 output file formats.

<table>
  <tr>
    <td align="center"><h6>Click Cell</h6></td>
    <td align="center"><h6>Select File</h6></td>
  </tr>
  <tr>
    <td><img src="http://i.imgur.com/OaDfzKV.png" alt="Click Cell"></td>
    <td><img src="http://i.imgur.com/sEmXMVX.png" alt="Select File"></td>
  </tr>
</table>

##### Link Discoverer -- Select Cross-Linkers

> **Selecting/Deselecting Cross-Linkers**
> Multiple cross-linkers can be selected per experiment (allowing "cocktail" cross-linker analysis), and all cross-linkers that are "checked" will be considered during the analysis. Simply click the cross-linker button to select or deselect it.
</blockquote>

<table>
  <tr>
    <td align="center"><h6>Check Crosslinker Button</h6></td>
  </tr>
  <tr>
    <td><img src="http://i.imgur.com/86v3b6i.png" alt="Select Crosslinker"></td>
  </tr>
</table>

##### Link Discoverer -- Run

> **Running XL Discoverer**
> Click run, which will produce a progress dialog, giving both the current progress and the current task. When it is done, it will make a quick report summary, stating the number of links identified as well as any errors during analysis. Click "close" to save the generated XL Discoverer report file.

<table>
  <tr>
    <td align="center"><h6>Press Run</h6></td>
    <td align="center"><h6>Click Close</h6></td>
    <td align="center"><h6>Save</h6></td>
  </tr>
  <tr>
    <td><img src="http://i.imgur.com/HQBW7Zu.png" alt="Press Run"></td>
    <td><img src="http://i.imgur.com/wDfqZdP.png" alt="Click Close", width="293", height="728"></td>
    <td><img src="http://i.imgur.com/30mj6kX.png" alt="Save"></td>
  </tr>
</table>

### ID & Quantitative Analysis -- Quantitative Link Discoverer

#### Menu Location

![Image of Quantitative Link Discoverer Splash Menu Location]
(http://i.imgur.com/Rk132DQ.png)

#### Overview

* Identifies cross-linked peptides and reports identically to Link Discoverer
* Quantifies each link identified
    * Automated peak identification
    * Capacity to manually filter for identified transitions
    * Save transition files for later and comparative analysis

#### Basic Use

**Not yet (fully) implemented**

### Quantitative Analysis -- MS/MS Quantitation

#### Menu Location

![Image of MSMS Quantitation Splash Menu Location]
(http://i.imgur.com/9MDaD8Z.png)

#### Overview

* Quantifies standard peptide transitions
    * Automated peak identification
    * Capacity to manually filter for identified transitions
    * Save transition files for later and comparative analysis

#### Basic Use

**Not yet implemented**

### Quantitative Analysis -- Load Transitions

#### Menu Location

![Image of Load Transitions Splash Menu Location]
(http://i.imgur.com/jdw2olC.png)

#### Overview

* Load and save transition files for manual spectral quantitation and validation
    * Inuitive user interface with separate lines for each isotope and charge state
    * Manual filter and refine peak selection
    * Load, save, and combine transition files for MS analysis

#### Basic Use

> **Analyzing Peptide Transitions**
> Through the file menu, open new transition files or add transitions to the current file. After opening a file, upon selecting a transition, the spectral intensities at each charge and isotopic state appear, along with the integration range (in black bars).

<table>
  <tr>
    <td align="center"><h6>Load</h6></td>
    <td align="center"><h6>Select Transition</h6></td>
    <td align="center"><h6>Adjust Range</h6></td>
  </tr>
  <tr>
    <td><img src="http://i.imgur.com/LyjqqhK.png" alt="Load"></td>
    <td><img src="http://i.imgur.com/Aa0AVLJ.png" alt="Select Transitions"></td>
    <td><img src="http://i.imgur.com/X5AUDty.png" alt="Adjust Range"></td>
  </tr>
</table>

## Input File Formats

### Input Types

> **Selecting Input Types**
> Currently, Protein Prospector is the only search database that accepts enough posttranslational modifications to enable facile cleavable, cross-linking mass spectrometry analysis, and it only supports level-separated product ion scans (or it tries to do MS/MS-level identification).
> Therefore, although XL Discoverer supports hierarchical scan formats, in practice, these are less practical to use than level-separated ones.

* Level Separated
    * Setting where each scan level (MS1, MS2, MS3) has a different file
    * Accepted file formats:
        - MGF, mzXML, mzML, PAVA
* Hierarchical
    * Where a single scan file encompasses all MS levels
    * Accepted file formats:
        - mzXML, mzML

### Compressed Files and File Archives

> **Compressed Files**
> XL Discoverer currently accepts a variety of compression types, including zipfiles (.zip), tarballs (.tar, .tar.gz, and .tar.bz2), bzip2-compressed files (.bz2) and gunzipped-files (.gz). Besides gunzipped and bzip2-compressed tarballs, no "doubly"-compressed files will be recognized.
> All compressed files may include only a single file (by design), so no batch archives may be submitted.

### Raw Scan Settings

* MS Scans (Hierarchical)
    * Raw scan file encompassing all MS scans
* MS2 Scans (Level Separated)
    * Precursor ion raw scan file
    * Example file formats:
        * *-2.mgf, *_FTMSms2cid.txt, *_ITMSms2cid_d.txt
* MS3 Scans (Level Separated)
    * Product ion raw scan file
    * Example file formats:
        * *-3.mgf, *_ITMSms3cid.txt, *_ITMSms3cid_c.txt, *_ITMSms3cid_link.txt

### Matched Peptide Output Settings

* MS3 Output
    * Matched peptides from the peptide search engine
    * Accepted file formats:
        * Protein Prospector
            - Tab-delimited text

#### Protein Prospector

##### Minimal Settings Example

![Image of Protein Prospector Output Page]
(http://i.imgur.com/aV62o7v.png)

##### Minimal Settings Explanation

> **Minimal Export Settings**
> These are the minimal settings with which you can export the matched peptides for XL Discoverer analysis. You can ALWAYS add more, however, you cannot subtract.

* Format Types
    * Tab-Delimited Text
* Score Settings
    * Min Score Protein
        * > 1 (1 is recommended)
    * Max E Value Peptide
        * > 1 (1 is recommended)
    * Min Score Protein
        * < 1 (1 is recommended)
    * Max E Value Peptide
        * < 1 (1 is recommended)
* Column Settings
    - M/Z
    - Charge
    - Error
    - Score
    - E Val
    - DB Peptide
    - Mod Reporting
        * "All Mods (1 Column)" OR "All Mods (2 Columns)"
    - Time
    - MSMS Info
    - Start AA
* Sort Settings
    * Peptide
* Report Settings
    * Expectation Value

## Advanced Settings

> **Advanced XL Discoverer Configurations**
> Details less-routine settings that enable to user to control advanced settings within XL Discoverer, such as adding new cross-linkers, customizing and editing reports, limiting and filtering for subproteomes, error thresholds for link discovery, and editing quantitation settings.

### Adding Custom Mods

> **Editing Custom Mods**
> This setting enables the user to add or remove custom mods, those not found in the standard peptide search database.

#### Adding New Mods

* **Formula**
    * Space-separated elements
    * Isotope number (optional) + atom symbol + count (optional)
    * Example:
        * 13C5 N-1 O 2H H15
* **Mod Name**
    * Mod name as it appears in the peptide search database
* **Reactivity**
    * CSV-separated 1-letter amino acids
    * Example:
        * D,E
        * K

![Image of Editing Custom Mods]
(http://i.imgur.com/V6tiNdl.png)

### Cross-Link Error Thresholds

> **Editing Error Thresholds**
> Link Discoverer has three tiers of cross-linked peptide discovery: standard, low-confidence, and potential multilink.
> Link Discoverer first tries to identify any standard interlinks, by sampling all masses up to a specific number above the monoisotopic mass and identifying if the theoretical and experimental masses are within the PPM threshold.
> If no standard cross-linked peptides are found, if the experimental mass is within a specified number of daltons of the theoretical mass, it reports a "low-confidence" cross-linked peptide.
> If no other cross-links are identified, there are 2 or more unique peptides identified from the same precursor scan, and the product ion masses sum to less than 300 Da of the precursor ion, a potential "multilink" is reported.

* Isotope Threshold
    * Integer number of isotopes above the monoisotopic to sample
        - Ex. an isotope threshold of 4 samples all isotope numbers from 0 to 4.
* PPM Threshold
    * Max error (integer, ppm) between the theoretical and experimental precursor ion for a standard cross-linked peptide ID.
* Mass Threshold
    * Max error (integer, daltons) between the theoretical and experimental precursor ion for a low-confidence cross-linked peptide ID

#### Submenu Location

![Image of Error Thresholds Submenu Location]
(http://i.imgur.com/GefmUcS.png)

### Protein Names and Filtering

#### Submenu Location

![Image of Protein Filtering Submenu Location]
(http://i.imgur.com/H5X7g6W.png )

#### Name and Filtering Categories

##### Greylist

> **Greylist Proteins**
> Proteins which are biologically present but likely irrelevant. Potential examples include the [CRAPome](http://www.crapome.org/) for affinity purification experiments. Proteins that are greylisted appear last in the XL Discoverer reports.

##### Blacklist

> **Blacklist Proteins**
> Proteins which are sample preparation artifacts, such as keratin, antibodies during immunoprecipitation, and trypsin. Scans containing peptides mapped back to these proteins are omitted during link identification.

##### Common Name

> **Common Proteins**
> Proteins which appear commonly in the researcher's samples or are of high interest to the researcher. These proteins are assigned a "common" name, a custom name preferentially used in the XL Discoverer reports.

##### Gene Name

> **Gene Database**
> Protein to gene name database stored locally, preventing UniProt database queries for proteins inside the database. Gene names are favored over UniProt IDs due to their conservation between species and logical nomenclature.

##### Limited Database

> **Custom Database**
> When activated, the limited database only searches for proteins within the defined database. If set to "mild", it only removes peptides which do not map back to proteins within the custom database. If set to strict, it removes all MS3 scans where one or more peptides could map to a protein outside of the limited database.

##### Decoy Database

> **Decoy Database**
> The decoy database contains a list of Protein Names and UniProt IDs, and reads all proteins from the database as decoys. This is useful for peptide search databases which do not specify a single "decoy" type, or while using a custom search database.

#### Batch Edit Protein Lists

> **Batch Editing Protein Lists**
> Due to the sheer size of the genome and proteome, the batch tools enable the efficient implementation of protein filters for proteomes for a given species, and proteins containing a specified substring.

* Add To Gene List
    * Add all proteins from a given species to the local gene database
* Remove From Gene List
    * Remove all proteins from a given species from the local gene database
* Edit Greylist
    * Add all proteins with a given substring from a given species to the greylist
    * A blank substring adds all proteins from that species
* Edit Blacklist
    * Add all proteins with a given substring from a given species to the blacklist
    * A blank substring adds all proteins from that species

##### Location

<table>
  <tr>
    <td><img src="http://i.imgur.com/MCoGPpF.png" alt="Link Discoverer Menu Location"></td>
    <td><img src="http://i.imgur.com/ddxQQHW.png" alt="Settings Location"></td>
  </tr>
</table>

#### Search Hits

> **Threshold for Search Inclusion**
> The large size of the totality of proteomes makes sub-database filtering crucial for proper identification in a search space, as well as for proper scoring parameters. Certain file formats, such as pep.XML, can report multiple search hits per file, and can be exported in filtered or unfiltered forms. XL Discoverer therefore can filter these search hits intrinsically, or extrinsically. If your are not filtering for a sub-database using XL Discoverer, it is recommended to turn off all search hits and **highly** recommended to use a filtered database, due to the reasons mentioned above.

##### Location

<table>
  <tr>
    <td><img src="http://i.imgur.com/MCoGPpF.png" alt="Link Discoverer Menu Location"></td>
    <td><img src="http://i.imgur.com/bEJDNYS.png" alt="Settings Location"></td>
  </tr>
</table>

### Customize Reports

**Not yet implemented**

#### Submenu Location

![Image of Customize Reports Submenu Location]
(http://i.imgur.com/IEBsonu.png)

### Editing Cross-Linkers

#### Location

<table>
  <tr>
    <td><img src="http://i.imgur.com/MCoGPpF.png" alt="Link Discoverer Menu Location"></td>
    <td><img src="http://i.imgur.com/aWv7Bc0.png" alt="Settings Location"></td>
  </tr>
</table>

#### Adding/Editing Cross-Linkers

> **Adding New Cross-Linkers**
> Click on the "New Cross-Linker" button, enter the cross-linker name and attributes, including the chemical formula of the fully-conjugated cross-linker, the charge of any lost reporter ions (if applicable), the number of reactive sites, the dead-end modifications upon cross-linker hydrolysis, and the number, name, and formula of the MS-cleaved fragments. Click save when finished to add it to the cross-linker list.

&nbsp;
> **Editing Cross-Linkers**
> Click on the button corresponding to the cross-linker name, and edit the characteristics. When finished, click "Save" to commit the changes.

![Image of Add New Cross-Linker Screen]
(http://i.imgur.com/Qnk5UJB.png)

#### Removing Cross-Linkers

> **Deleting a Cross-Linker**
> In case an entered cross-linker is no longer used by your lab, you can always remove the cross-linker. Simply click "Delete Cross-Linker", click on the cross-linker, and it will removed.

### Edit Column Order

#### Location

<table>
  <tr>
    <td><img src="http://i.imgur.com/MCoGPpF.png" alt="Link Discoverer Menu Location"></td>
    <td><img src="http://i.imgur.com/woCVW0I.png" alt="Settings Location"></td>
  </tr>
</table>

#### Editing a Report's Column Order

> **Changing Column Ordering**

> The reports, due to the *n* linked possible peptides, are dynamically generated using "blocks". Each block sequentially adds columns to the report, and can be "static", "sequential", or "clustered". Blocks can be added or removed, enabling highly customizable report formats.

> **Static**

> Each column within the block is added directly the spreadsheet, i.e., without any suffixes. Static columns cannot be used with peptide-level data (such as the product ion PPM, expectation value, or score).

> **Sequential**

> For each <i>i</i> peptide in {1, ..., *n*}, each column in the block is sequentially added to the spreadsheet, with a suffix ("A", "B", ...) if the maximum number of linked peptides in that report *n* is larger than 1.

> **Clustered**

> For each column in the block, the column is added *n* times to the spreadsheet before adding another column. The columns will have a similar suffix to the "Sequential" blocks.

&nbsp;
> **Moving Columns**

> Drag and drop a column to move an individual column between or within a block. The screen will automatically scroll when the cursor approaches the edge of the application while dragging a column.

&nbsp;
> **Adding/Removing Columns**

> The "Unused" block determines columns that are ignored during report creation. To add a column to the report, drag that column from "Unused" to another block, and to remove it, drag it back to "Unused".

&nbsp;
> **Previewing the Order**

> Clicking on "Preview" creates a popup which shows a sample column order in a table to preview how the report would look in the spreadsheet.

![Image of the Editing Column Order Screen]
(http://i.imgur.com/rjAgIwY.png)

#### Toggling the Comparative Report

> **Options**

> The comparative uses a hierarchical header, with grouping by cross-linker or by filename, with filename grouping by default. To change this, go to the settings menu and switch between "Files" or "Crosslinkers".

![Image of the Toggling the Comparative Group Order]
(http://i.imgur.com/48HJgVv.png)

## Report Descriptions

### Interlinks

> The interlink report lists all cross-linked peptides identified with more than 1-linked peptide. These cross-links are segregated, with the greylisted proteins appearing at the bottom of the report.

![Image of the Interlinks report]
(http://i.imgur.com/CyDGnTl.png)

### Quantitative

> The quantitative report lists all cross-linked peptides identified that were selected for quantitative analysis. The cross-linked peptide information, along with the spectral intensities, is listed in a format similar to the "Interlinks" report.

![Image of the Quantitative report]
(http://i.imgur.com/2kchEH8.png)

### Transitions

> A single-sheet report generated from the "Load Transitions" menu, which is generated upon exported the transition-list intensities to file. The report format is similar to the "Interlinks" report.

![Image of the Transitions report]
(http://i.imgur.com/aMuMXDl.png)

### Best IDs -- All | File

> The "Best IDs" reports list either the best identified cross-linked peptides for the whole comparison (All) or per file analyzed (File). The peptides are weighted by their scoring parameters, including PPM, expectation value, and peptide score.
> All peptides with the same non-cross-linker modifications and the same intact cross-linker number and modified residues are considered unique pairs. For example, a cross-linked peptide KRASSER-LINKER with serine-phospho group for one would be considered different than the cross-linked peptide without the phospho group.

![Image of the Best IDs report]
(http://i.imgur.com/qWXGPQ5.png)

### Comparative

> The comparative report generates a spreadsheet with the file names and cross-linkers as columns, and the linkages as rows, allowing a visual comparison between cross-linked peptide coverage between various samples. This report can also be filtered for "common" proteins, those entered in [Common Name](#common-name). Greylisted proteins appear at the bottom of the report.

![Image of the COmparative report]
(http://i.imgur.com/rPPqlVX.png)

### Skyline

> The Skyline report processes the cross-linked peptides and their mods for importation to Skyline, to make use of the quantitation tools there. Specifically, the Skyline report linearizes the cross-linked peptide, converts the mod names to [+Mass]-format, and then outputs them in a column for easy Skyline importation.

![Image of the Skyline report]
(http://i.imgur.com/JUPPh2Y.png)

### Low Confidence

> A report similar to "Interlinks" with all the low-confidence interlinks, those not within the PPM threshold for any of the isotopes samples, but within the mass theshold specified. Similarly, greylisted proteins appear at the bottom of the report.

![Image of the Low Confidence report]
(http://i.imgur.com/0Xsveku.png)

### Mutlilinks

> A report similar to "Interlinks" with all the potential multilinks, multiple, different sequenced peptides that appear from a single precursor scan but do not mass close to the precursor ion.

![Image of the Multilinks report]
(http://i.imgur.com/NJGuQpe.png)

### Singles

> A report with all the "single" peptides with cross-linker modifications, that do not match any link type.

![Image of the Singles report]
(http://i.imgur.com/HdL41YM.png)

### Deadends

> A report with a single peptide per scan where each cross-linker on the peptide is only conjugated on one end.

![Image of the Deadends report]
(http://i.imgur.com/eAGKA6j.png)

### Intralinks

> A report with a single peptide per scan where at least one peptide on the cross-linker is conjugated at more than one end.

![Image of the Intralinks report]
(http://i.imgur.com/FBpiL4y.png)

### General Report

> An overall report listing all the identified links (interlinks, deadends, intralinks, singles, low-confidence links, and potential multilinks, sorted by file, cross-linker, and then sequential scans).

![Image of the General Report]
(http://i.imgur.com/qhTw03t.png)

## Testing

* Run basic, repeatable, fast system tasks to ensure system utilities are working.
* All automated through a central script or command-line utility.

To use the testing features, either run "run_tests.py" or the following script in the XL Discoverer directory:

```
python -m unittest discover --verbose test
```

### Checked Features

1. QWidget functions and subclasses
2. Data storage via custom data structures
3. Matched Peptide recognition and parsers
  * Tab-delimited text
  * XML
4. Raw scan recognition and parsers
  * mzXML
  * mzML
  * MGF
  * PAVA
5. Mod recognition and parsing
6. Link searching and identification
  * Discrimination between link forms
  * Rejection of non-cross-linked peptides
7. Output writers
  * xiNet writer
  * Skyline mod writers
  * Mods in peptide and mod writers
8. Test spreadsheet creation globally
  * Comparative
  * Best Peptide
  * Interlink/Intralink/Deadend Report
  * XL Discoverer Report
  * Skyline
9. XL Discoverer logs FTP/Stream handlers
10. FTP connection and login for log storage
11. Statistical and other mathematical functions
12. HTTP connection for UniProt KB queries

## Updates

> **Binaries enable automatic updates**

> In order to do so, you need a GitHub authorization token and account. [Get an authorization token](https://help.github.com/articles/creating-an-access-token-for-command-line-use/) and then open configs/private.json and replace the nulls with your username and authentification token (in quotes, so "Alexhuszagh" would be my username).

**private.json**

<table>
  <tr>
    <td align="center"><h6>Before</h6></td>
    <td align="center"><h6>After</h6></td>
  </tr>
  <tr>
    <td><img src="http://i.imgur.com/8IfMGhj.png" alt="Before"></td>
    <td><img src="http://i.imgur.com/K3ngJvy.png" alt="After"></td>
  </tr>
</table>
