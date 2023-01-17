from hashlib import md5
import os
from pathlib import Path
import platform
from types import FunctionType
from pydofus2.com.ankamagames.dofus import Constants
from pydofus2.com.ankamagames.dofus.logic.connection.managers.AuthentificationManager import (
    AuthentificationManager,
)
from pydofus2.com.ankamagames.dofus.logic.shield.ShieldCertifcate import ShieldCertifcate
from pydofus2.com.ankamagames.dofus.logic.shield.ShieldSecureLevel import ShieldSecureLevel
from pydofus2.com.ankamagames.dofus.network.types.secure.TrustCertificate import TrustCertificate
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.managers.StoreDataManager import StoreDataManager
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray
from pydofus2.com.ankamagames.jerakine.types.CustomSharedObject import CustomSharedObject
from flash.Capabilities import Capabilities

logger = Logger("Dofus2")


class SecureModeManager(metaclass=Singleton):

    # shieldApi:ShieldApi

    _active: bool

    _hasV1Certif: bool

    _validateCodeCallback: FunctionType

    shieldLevel: int

    def __init__(self):
        self.shieldLevel = StoreDataManager().getSetData(
            Constants.DATASTORE_COMPUTER_OPTIONS,
            "shieldLevel",
            ShieldSecureLevel.MEDIUM,
        )

    @property
    def active(self) -> bool:
        return self._active

    @active.setter
    def active(self, b: bool) -> None:
        logger.debug("SECURE MODE IS ACTIVE : " + b)
        self._active = b

    @property
    def certificate(self) -> TrustCertificate:
        return self.retreiveCertificate()

    def getUsername(self) -> str:
        return AuthentificationManager().username.lower().split("|")[0]

    def getCertifFolder(
        self,
        version: int,
        useCustomSharedObjectFolder: bool = False,
        useMacApplicationDirectory: bool = False,
    ) -> Path:

        if not useCustomSharedObjectFolder:
            parentDir = Path(os.getenv("APPDATA"))
        else:
            parentDir = CustomSharedObject().getCustomSharedObjectDirectory()
        if version == 1:
            f = parentDir / "AnkamaCertificates"
        if version == 2:
            f = parentDir / "AnkamaCertificates/v2-RELEASE"
        os.makedirs(f, exist_ok=True)
        return f


    def getCertificateFile(self) -> Path:
        try:
            found = False
            userName = self.getUsername()
            fileName = md5(userName.encode()).hexdigest()
            f = self.getCertifFolder(2) / fileName
            if not f.exists():
                f = self.getCertifFolder(2, False, True) / fileName
            else:
                found = True
                logger.debug("CERTIF FOUND IN V2-RELEASE : " + str(f.absolute()))
            if not found:
                if not f.exists():
                    f = self.getCertifFolder(1) / fileName
                else:
                    found = True
                    logger.debug("CERTIF FOUND IN MAC APPLICATION DIRECTORY" + str(f.absolute()))
            if not found:
                if not f.exists():
                    f = self.getCertifFolder(1, False, True) / fileName
                else:
                    found = True
                    logger.debug("CERTIF FOUND IN V1" + str(f.absolute()))
            if not found:
                if not f.exists():
                    f = self.getCertifFolder(2, True) / fileName
                else:
                    found = True
                    logger.debug("CERTIF FOUND IN V1 ON MAC" + str(f.absolute()))
            if not found:
                if not f.exists():
                    f = self.getCertifFolder(1, True) / fileName
                else:
                    found = True
                    logger.debug("CERTIF FOUND IN CUSTOM SHARED OBJECTS V2" + str(f.absolute()))
            if not found and f.exists():
                found = True
                logger.debug("CERTIF FOUND IN CUSTOM SHARED OBJECTS V1" + str(f.absolute()))
            if not found:
                logger.debug("CERTIF NOT FOUND")
            if f.exists:
                return f
        except Exception as e:
            logger.error("Erreur lors de la recherche du certifcat : " + str(e))
        return None

    def retreiveCertificate(self) -> TrustCertificate:
        logger.debug("TRY TO RETREIVE CERTIFICATE")
        try:
            self._hasV1Certif = False
            f = self.getCertificateFile()
            if f:
                with open(f, "rb") as fs:
                    certif: ShieldCertifcate = ShieldCertifcate.fromRaw(ByteArray(fs.read()))
                if certif.id == 0:
                    logger.error("Certificat invalide (id=0)")
                    return None
                if certif.version < 4 and (Capabilities.os == "Windows 10" or "Darwin" in Capabilities.os):
                    self._hasV1Certif = True
                logger.debug("RETREIVE CERTIFICATE :: RETRIEVED")
                return certif.toNetwork()
        except Exception as e:
            logger.debug("RETREIVE CERTIFICATE :: ERROR " + str(e))
            raise Exception("Impossible de lire le fichier de certificat.", e)
        return None
    