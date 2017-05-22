# Xl Discoverer

**Table of Contents**

- [Requirements](#requirements)
  - [Binary Installation](#binary-installation)
    - [Detailed Directions (Binary)](#detailed-directions-binary)
  - [Using Python Source](#using-python-source)
    - [Detailed Directions (Python Source)](#detailed-directions-python-source)
      - [Windows](#windows)
      - [Mac OS X/Linux](#mac-os-xlinux)
- [Motivation](#motivation)
- [Tutorial](#tutorial)
- [Change Log](#change-log)
- [Contributors](#contributors)
- [License](#license)

## Requirements

### Binary Installation

Should work with no dependencies.

#### Detailed Directions (Binary)

1. Download the binary and extract it, keeping the directory structure intact.
2. Make sure all files are executable
    * On Windows, this should be default
    * On Linux/Mac OS X, this should be:
    ```
    chmod +x <file>
    ```
3. Execute the program

### Using Python Source

* [Python 2.7 or 3.4](https://www.python.org/download/releases/2.7/)
* [pip](https://pip.pypa.io/en/latest/installing.html)
* [Wheel] (https://pypi.python.org/pypi/wheel)
* [PySide] (https://pypi.python.org/pypi/PySide)
* [NumPy] (https://pypi.python.org/pypi/numpy)
* [SciPy] (http://www.scipy.org/)
* [six] (https://pythonhosted.org/six/)
* [Cython] (http://cython.org/)
* [Numexpr] (https://github.com/pydata/numexpr)
* [PyTables] (http://www.pytables.org/)
* [Requests] (http://docs.python-requests.org/en/master/)
* [XlsxWriter] (https://pypi.python.org/pypi/XlsxWriter)

**OR**
* [OpenPyXl] (https://pypi.python.org/pypi/openpyxl)

#### Detailed Directions (Python Source)

1. Make sure Python is added to the path, or type the full path to the Python executable.
2. Install pip by downloading get-pip.py
3. Just run the binary and then install Wheel.
4. For PySide, Six, Requests, and XlsxWriter (or OpenPyXl), install with, replacing "<package>" with the package name.
    ```
    python -m pip install <package>
    ```

5. NumPy, SciPy, Numexpr, and PyTables:
    * Windows Only: Download wheel files from http://www.lfd.uci.edu/~gohlke/pythonlibs/
        * Do NOT rename the wheel files
        * Run the above installer command, replacing "<package>" with full path to the wheel file
    * Mac OS X/Linux: Install these packages via pip
6. Launch xldiscoverer.pyw with any Python launcher.
    * Ex:.
    *
    ```
    python xldiscoverer.pyw
    ```

##### Windows

```
python get-pip.py
python -m pip install wheel
python -m pip install PySide, XlsxWriter, requests, six
python -m pip install numpy-package.whl
python -m pip install cython-package.whl
python -m pip install numexpr-package.whl
python -m pip install scipy-package.whl
python -m pip install pytables-package.whl
```

##### Mac OS X/Linux

```shell
python get-pip.py
sudo pip install wheel
sudo pip install PySide, XlsxWriter, requests
sudo pip install cython numpy scipy numexpr pytables
```

## Tutorial

[Tutorial To XL Discoverer](https://github.com/Alexhuszagh/xltools/blob/master/Tutorial.md)

## Motivation

Although the advancement of cross-linking mass spectrometry and its application to the analysis of protein complexes *in vivo* have been tremendous, the lack of automated tools for MS identification and quantification have stalled its growth. Xl Discoverer aims to provide an automated framework in a standalone application for crosslinking mass spectrometry identification and analysis.

## Change Log

## Contributors

* Alex Huszagh

## License

Copyright (C) 2015 Alex Huszagh <https://github.com/Alexhuszagh/xltools/>

XL Discoverer is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This xlDiscoverer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with xlDiscoverer. If not, see <http://www.gnu.org/licenses/>.
