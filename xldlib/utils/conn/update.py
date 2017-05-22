'''
    Utils/conn/update
    ____________

    Find new releases via GitHub's API by tag and execs an update
    if suitable.

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load future
from __future__ import division

# load modules
import json
import os
import platform
import shutil
from ssl import CertificateError
import stat
import sys
import tarfile
import zipfile

from PySide import QtCore, QtGui
import requests

from models import config, params
from xldlib import resources
from xldlib.definitions import HTTPError, Request, URLError, urlopen
from xldlib.qt.objects import base
from xldlib.utils import logger

# load objects/functions
from xldlib.definitions import partial
from gui.views.update import DownloadDialog, Git
from .certs import SSLCerts

# ------------------
#      RELEASES
# ------------------


class ProcessRelease(base.BaseObject):
    '''Extracts and shutils binary releases for XL Discoverer'''

    installed = QtCore.Signal(bool)

    _split = {'Windows': '.exe', 'Darwin': ('.dmg', '.app')}

    def __init__(self, parent=None):
        '''
        Call parent class and bind instance attributes, include
        tags for URLs and headers for GET requests.
        '''
        super(ProcessRelease, self).__init__(parent)

        logger.Logging.info("Initializing ProcessRelease...")

    # ------------------
    #        MAIN
    # ------------------

    @staticmethod
    def extract_archive(name, fileobj, path, version):
        '''
        Gets the archive schema from the name and extracts the latest
        binary to file.
        :
            name -- release name, IE, "Linux.zip"
            fileobj -- open fileobj from streaming request
            path -- appdata path to extract to
            version -- version info, IE, '0.0.6', to extract the file to
            extract_archive('Linux.zip', <file>, 'path/to/file', '0.0.5')
                ->void
        '''

        # can't use os.path.splitext because of tar.gz/tar.bz2
        if name.endswith('.zip'):
            ProcessRelease.extract_zip(fileobj, path, version)
        elif name.endswith('tar.gz') or name.endswith('tar.bz2'):
            ProcessRelease.extract_tar(fileobj, path, version)

    @staticmethod
    def extract_zip(fileobj, path, version):
        '''
        Extracts the binary file from a zipfile archive
        :
            fileobj -- open fileobj from streaming request
            path -- appdata path to extract to
            version -- version info, IE, '0.0.6', to extract the file to
            extract_zip(<file>, 'path/to/file', '0.0.5')->void
        '''

        # find newest entry in archive
        fileobj.seek(0)
        archive = zipfile.ZipFile(fileobj, mode='r')
        names = [i for i in archive.namelist() if config.APP_DATA in i]
        newest = max(names, key=ProcessRelease._latest_key)

        # extract member to path
        member = archive.open(newest)
        dst = os.path.join(path, 'v_{0}'.format(version))
        target = open(dst, "wb")
        shutil.copyfileobj(member, target)

        archive.close()
        ProcessRelease._add_exec_permissions(dst)

    @staticmethod
    def extract_tar(fileobj, path, version):
        '''
        Extracts the binary file from a tarball archive
        :
            fileobj -- open fileobj from streaming request
            path -- appdata path to extract to
            version -- version info, IE, '0.0.6', to extract the file to
            extract_tar(<file>, 'path/to/file', '0.0.5')->void
        '''

        # find newest entry in archive
        fileobj.seek(0)
        archive = tarfile.open(fileobj=fileobj)
        names = [i for i in archive.getnames() if config.APP_DATA in i]
        newest = max(names, key=ProcessRelease._latest_key)

        # extract member to path
        member = archive.getmember(newest)
        name = 'v_{0}'.format(version)
        member.name = name
        archive.extract(member, path)

        archive.close()
        ProcessRelease._add_exec_permissions(os.path.join(path, name))

    # ------------------
    #    FILE UTILS
    # ------------------

    @staticmethod
    def _add_exec_permissions(path):
        '''
        Adds executable permissions to a file
        :
            path -- full path to file
            _add_exec_permissions('path/to/file')->void
        '''

        st_mode = os.stat(path).st_mode
        os.chmod(path, st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

    @staticmethod
    def _latest_key(name):
        '''
        Grabs the latest version within an archive
        :
            name -- filename with archive
            _latest_key('appdata/v_0.0.5')->(0, 0, 5)
        '''

        name = os.path.basename(name)
        return GetReleases.split_version(name)

    @staticmethod
    def split_version(version, prefix=True):
        '''
        Splits the version for comparisons
        :
            split_version("0.0.6")->(0, 0, 6)
        '''

        if prefix:
            for os_, ext in ProcessRelease._split.items():
                if platform.system() == os_ and version.endswith(ext):
                    version = os.path.splitext(version)[0]

            version = version.split('_')[1]
        return tuple((int(i) for i in version.split('.')))


class GetReleases(ProcessRelease):
    '''Finds all binary releases for XL Discoverer'''

    headers = {"Accept": "application/octet-stream"}
    base_keys = Git.base_keys
    url_keys = Git.url_keys
    _queued = qt.CONNECTION['Queued']

    def __init__(self, parent=None, **kwargs):
        '''
        Call parent class and bind instance attributes, include
        tags for URLs and headers for GET requests.
        '''
        super(GetReleases, self).__init__(parent)

        self.git = Git()
        self.server = kwargs.get('server') or resources.GIT_SERVER
        self.tags = kwargs.get("tags") or self.git['tags']
        self.releases = kwargs.get('releases') or self.git['releases']

        name = kwargs.get('name') or "GitHub"
        self.user = params.PRIVATE[name]['username']
        self.token = params.PRIVATE[name]['token']
        self.headers.update({"Authorization": "token {0}".format(self.token)})

        logger.Logging.info("Initializing GetReleases...")

    # ------------------
    #        MAIN
    # ------------------

    @logger.except_error((URLError, IOError, SyntaxError, IndexError))
    def get_latest(self):
        '''
        Get the latest XL Discoverer release.
        :
            get_latest()->{u'commit': ..., 'name': '0.0.5'}
        '''

        if not hasattr(self, "latest"):
            tags = self._tags()
            if tags is not None:
                logger.Logging.info("Got the commit information for XL Discoverer")
                release = self._stable_release(tags)
                setattr(self, "latest", release)

        if hasattr(self, "latest"):
            return self.latest

    @logger.except_error((URLError, IOError, SyntaxError))
    def get_latest_release(self):
        '''
        Gets a defined release or the user-defined release based
        on the system architcture.
        :
            get_latest_release()->
                {..., 'assets': [{'name': 'Linux.zip'}, ...]}
        '''

        latest = self._releases()
        logger.Logging.info("Got the latest release info for XL Discoverer")
        if latest:
            if isinstance(latest, list):
                latest = latest[0]

        return latest

    def get_release_worker(self):
        '''
        Grabs the latest releases binary for the system architecture
        :
            get_release_worker()->DownloadDialog(response)
        '''

        # grab release candidates
        latest = self.get_latest_release() or {'assets': []}
        version = latest.get('tag_name', '0.0.0')
        candidates = latest['assets']
        system = platform.system().lower()

        for candidate in candidates:
            name = candidate['name']
            if name.lower().startswith(system):
                # grab our response from the GitHub asset asset
                return self._find_candidate(candidate, name, version)

        # no builds found for the current system
        msg = config.MESSAGES['noWorker']
        self.exec_msg(parent=self.app.mainframe(), **msg)

    # ------------------
    #    REST UTILS
    # ------------------

    @staticmethod
    def _stable_release(tags):
        '''Returns the latest stable release (no dev, rc in last number)'''

        count = 0
        release = tags[count]
        while not release['name'].split('.')[-1].isdigit():
            # need to skip dev versions, which have 0.2.3dev1 format
            count += 1
            release = tags[count]

        return release

    def _request(self, url):
        '''
        Grabs the GET request for urllib2/urllib.request and adds
        authentification
        :
            _request('https://api.github.com/...')-><urllib2.Request ...>
        '''

        request = Request(url)
        if self.token:
            request.add_header("Authorization", "token {0}".format(self.token))
        return request

    @logger.except_error((CertificateError, HTTPError))
    def _tags(self):
        '''
        Grabs the tags for XL Discoverer releases.
        :
            _tags()->[{'commit': ..., 'name': 0.0.5}, ...]
        '''

        request = self._request(self.tags)
        response = urlopen(request, timeout=1)
        return self._todict(response)

    @logger.except_error((CertificateError, HTTPError))
    def _releases(self):
        '''
        Gets the releases for XL Discoverer.
        :
            _releases()->{'body': ...., 'tag_name': '0.0.5'}
        '''

        request = self._request(self.releases)
        response = urlopen(request, timeout=1)
        return self._todict(response)

    @staticmethod
    def _todict(response):
        '''Converts and returns a successful HTML request to a dict'''

        if response.code == 200:
            obj = json.loads(response.read().decode('utf-8'))
            response.close()
            return obj

    def _release_url(self, key, asset_id):
        '''
        Grabs the candidate release URL for downloading
        :
            _release_url('assets', 707843)->u'<self.releases>/assets/707843'
        '''

        return self.git[key] + self.server['path'] + str(asset_id)

    @logger.except_error(requests.exceptions)
    def _get_binary(self, url):
        '''
        Streams the candidate URL to bytes and initiates a
        QProgressBar to keep the APP response.
        :
            _get_binary('<self.releases>/assets/707843')->
                DownloadDialog(response)
        '''

        cert_path = SSLCerts()
        kwds = {'headers': self.headers, 'stream': True}
        try:
            response = requests.get(url, verify=cert_path, **kwds)

        except requests.exceptions.SSLError:
            # no luck, cert_path is incapable
            logger.Logging.warning("Invalid SSL certificate...")
            response = requests.get(url, verify=False, **kwds)

        if not response.ok:
            # requests library doesn't default to exception handling
            response.raise_for_status()

        else:
            return DownloadDialog(response, self.app.mainframe())

    def _process_buffer(self, name, buf, path, version):
        '''
        Connection signal to thread termination.
        :
            name -- release name, IE, "Linux.zip"
            fileobj -- open fileobj from streaming request
            path -- appdata path to extract to
            version -- version info, IE, '0.0.6', to extract the file to
            _process_buffer('Linux.zip', <_io.BytesIO ...>,
                            '/path/to/dir', '0.0.5')->void
        '''

        if buf is not None:
            path = config.DIRS['home']
            self.extract_archive(name, buf, path, version)
        self.installed.emit(True)

    def _find_candidate(self, candidate, name, version):
        '''Finds the candidate release worker from the candidates list'''

        asset_id = candidate['id']
        url = self._release_url('assets', asset_id)
        cls = self._get_binary(url)
        func = partial(self._process_buffer, name,
                       cls.buf, config.APP_DATA, version)
        cls.finished.connect(partial(cls.fin, func), self._queued)
        return cls

# ------------------
#      UPDATER
# ------------------


class Updater(QtCore.QObject):
    '''Checks whether a suitable installation candidate can be found'''

    def __init__(self, parent=None):
        super(Updater, self).__init__(parent)

        self.releases = GetReleases(self)
        self.latest = self.releases.get_latest() or {'name': '-200.0.0'}
        self.releases.installed.connect(self._close)

    # ------------------
    #        MAIN
    # ------------------

    def check(self):
        '''
        Checks whether a candidate install can be found. If no
        suitable GitHub authorization keys are found, this will return
        false.
        :
            check()->True
        '''

        # only update if frozen
        if getattr(sys, 'frozen', False):
            version = self.latest.get('name', '-200.0.0')
            latest = GetReleases.split_version(version, False)
            current = GetReleases.split_version(version.BUILD, False)

            if latest > current:
                return True
        return False

    def install_update(self):
        '''
        Adds a candidate update from the GitHub repository to the
        appdata folder and then queues the launcher to use the new
        version.
            install_update()->void
        '''

        cls = self.releases.get_release_worker()
        cls.show()

    # ------------------
    #       UTILS
    # ------------------

    @staticmethod
    def _close():
        '''
        Closes the MainApplication and connects it to the system exit.
        :
            _close()->sys.exit()
        '''

        QtGui.QApplication.closeAllWindows()
        QtGui.QApplication.exit(config.EXIT_CODES['install'])
        QtGui.QApplication.processEvents()
        sys.exit(config.EXIT_CODES['install'])

# ------------------
#   CONFIGURATIONS
# ------------------


def config_updater():
    '''
    Core updater for the first run after an update. Will change version
    to version, while update_configurations will not.
    '''


def update_configurations():
    '''
    Runs update scripts which enable the updating of configuration
    settings from previous glitched values.
    '''

    if version.VERSION not in version.VERSIONS:
        # first need to delete all versions
        current = GetReleases.split_version(version.VERSION, prefix=False)
        for key in list(version.VERSIONS.keys()):
            old = GetReleases.split_version(key, prefix=False)
            if old < current:
                del version.VERSIONS[key]

        config_updater()
        version.VERSIONS[version.VERSION] = None

# call the update scripts on load
update_configurations()
