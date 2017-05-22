'''
    Utils/conn/certs
    ________________

    Locates the path of the SSL certificates, usually cacert.pem

    :copyright: (c) 2015 The Regents of the University of California.
    :license: GNU GPL, see licenses/GNU GPLv3.txt for more details.
'''

# load modules
import os
import sys

import requests

# ------------------
#   SSL CERT PATH
# ------------------


class SSLCerts(str):
    '''Class object which returns the SSL cert paths'''

    # resource holder for the PyInstaller temp path
    _meipass = getattr(sys, '_MEIPASS', os.path.realpath("."))

    def __new__(cls, cert='cacert.pem'):
        return super(SSLCerts, cls).__new__(cls, cls.cert_path(cert))

    # ------------------
    #      PUBLIC
    # ------------------

    @classmethod
    def resource_path(cls, relative):
        '''Returns the exact path to a given resource'''

        return os.path.join(cls._meipass, relative)

    @classmethod
    def cert_path(cls, cert):
        '''Returns the absolute path to cacert.pem for http queries'''

        if getattr(sys, "frozen", False):
            return cls.resource_path(cert)
        else:
            return requests.certs.where()
