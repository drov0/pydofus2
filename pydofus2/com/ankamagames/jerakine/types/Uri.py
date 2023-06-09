import os
from pathlib import Path
from urllib.parse import urlparse, unquote
import hashlib
from pydofus2.com.ankamagames.dofus import Constants
from pydofus2.com.ankamagames.jerakine.managers.LangManager import LangManager
import platform

_osIsWindows = platform.system() == "Windows"
class Uri:
    def __init__(self, uri=None):
        self._protocol = None
        self._path:str = None
        self._subPath:str = None 
        self._secureMode = False  # Assuming secure mode to be False initially
        self._useSecureURI = False  # Assuming use secure URI to be False initially
        self._uri = uri        
        self._uriChanged = True
        self._fileNameChanged = True
        self._fileTypeChanged = True
        self.parseUri(uri)

    def parseUri(self, uri:str):
        if not uri:
            return
        signPos = uri.find('://')
        pathWithoutProtocol = None
        if signPos != -1:
            protocolStart = uri.rfind('://', 0, signPos)
            if protocolStart == -1:
                self._protocol = uri[0:signPos]
            else:
                self._protocol = uri[protocolStart+3:signPos]
            pathWithoutProtocol = uri[signPos + 3:]
        else:
            self._protocol = 'file'
            pathWithoutProtocol = uri

        signPos = pathWithoutProtocol.find('|')
        if signPos == -1:
            self.path = pathWithoutProtocol
        else:
            self.path = pathWithoutProtocol[0:signPos]
        if signPos != -1 and len(pathWithoutProtocol) > signPos + 1:
            self.subPath = pathWithoutProtocol[signPos + 1:]
        else:
            self.subPath = None
        if self._secureMode and self._useSecureURI and self._protocol == 'file' and not self.isSecure():
            raise ValueError(f"'{uri}' is an insecure URI.")

    def isSecure(self):
        # This needs to be implemented according to your requirements
        return True

    def toString(self):
        return f"{self._protocol}://{self._path}" + (f"|{self._subPath}" if self._subPath else "")

    def toSum(self):
        return hashlib.md5(self.toString().encode()).hexdigest()

    @property
    def protocol(self):
        return self._protocol

    @protocol.setter
    def protocol(self, value):
        self._protocol = value
        self._uri = self.toString()

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, value:str):
        i = 0
        if "\\" in value:
            self._path = value.replace("\\", "/")
        else:
            self._path = value
        if _osIsWindows:
            if self._path.startswith("/"):
                for i in range(1, len(self._path)):
                    if self._path[i] != "/":
                        break
                self._path = "\\\\" + self._path[i:]
            if "//" in self._path:
                self._path = self._path.replace("//", "/")
        self._sum = ""
        self._uriChanged = True
        self._fileNameChanged = True
        self._fileTypeChanged = True
        
    @property
    def subPath(self):
        return self._subPath

    @subPath.setter
    def subPath(self, value):
        if (not self.subPath and not value) or (self.subPath and value and len(self.subPath) == len(value) and self.subPath.startswith(value)):
            return
        if value is None or value == "":
            self._subpath = None
        else:
            self._subpath = value[1:] if value[0] == "/" else value
        self._sum = ""
        self._uriChanged = True
        self._fileNameChanged = True
        self._fileTypeChanged = True

    @property
    def uri(self):
        return self._uri

    @uri.setter
    def uri(self, value):
        self.parseUri(value)

    def toFile(self) -> Path:
        if not self._path:
            tmp = "null"
        else:
            tmp = self._path

        if _osIsWindows and (tmp.startswith("\\\\") or tmp[1] == ":"):
            return Path(tmp)

        if not _osIsWindows and tmp[0] == "/":
            return Path("/" + tmp)

        if self._protocol == "mod":
            uiRoot = LangManager().getEntry("config.mod.path")

            if not (uiRoot.startswith("\\\\") or uiRoot[1:3] == ":/"):
                return Constants.DOFUS_ROOTDIR / Path(uiRoot) / Path(tmp)
            
            return Path(uiRoot) / Path(tmp)

        return Constants.DOFUS_ROOTDIR / Path(tmp)

    @property
    def fileType(self):
        if self._fileTypeChanged:
            if not self._subPath or not "." in self._subPath:
                pointPos = self._path.rfind(".")
                paramPos = self._path.find("?")
                self._fileType = self._path[pointPos + 1 : paramPos if paramPos != -1 else float("inf")]
            else:
                self._fileType = self._subPath[self._subPath.rfind(".") + 1 : self._subPath.find("?") if self._subPath.find("?") != -1 else float("inf")]

            self._fileTypeChanged = False
        return self._fileType



