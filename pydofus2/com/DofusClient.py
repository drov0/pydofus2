import sys
import threading
import tracemalloc
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import (
    KernelEventsManager,
    KernelEvts,
)
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReason import DisconnectionReason
from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
from time import perf_counter, sleep
import pydofus2.com.ankamagames.dofus.kernel.Kernel as krnl
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import (
    DisconnectionReasonEnum,
)
from pydofus2.com.ankamagames.dofus.logic.connection.actions.LoginValidationWithTokenAction import (
    LoginValidationWithTokenAction,
)
import pydofus2.com.ankamagames.dofus.logic.connection.managers.AuthentificationManager as auth
import pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler as connh
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from pydofus2.com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from pydofus2.com.ankamagames.jerakine.data.I18nFileAccessor import I18nFileAccessor
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from typing import TYPE_CHECKING
from pydofus2.com.ankamagames.jerakine.logger.MemoryProfiler import MemoryProfiler
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.jerakine.network.ServerConnection import ServerConnection
from pydofus2.com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider

logger = Logger()


class DofusClient(metaclass=Singleton):
    LOG_MEMORY_USAGE: bool = False
    _stop = threading.Event()
    _stopReason: DisconnectionReason = None
    _lastLoginTime = None
    _minLoginInterval = 10
    _joined = False

    def __init__(self):
        krnl.Kernel().init()
        logger.info("Kernel initialized ...")
        self._worker = krnl.Kernel().getWorker()
        self._registredInitFrames = []
        self._registredGameStartFrames = []
        I18nFileAccessor().init()
        DataMapProvider().init(AnimatedCharacter)
        logger.info("DofusClient initialized")

    def login(self, loginToken, serverId=0, characterId=None):
        if self._lastLoginTime is not None and perf_counter() - self._lastLoginTime < self._minLoginInterval:
            logger.info("Login request too soon, will wait some time")
            sleep(self._minLoginInterval - (perf_counter() - self._lastLoginTime))
        if krnl.Kernel().wasReseted:
            krnl.Kernel().init()
        self._lastLoginTime = perf_counter()
        if self.LOG_MEMORY_USAGE:
            tracemalloc.start(10)
        self._serverId = serverId
        self._characterId = characterId
        self._loginToken = loginToken
        auth.AuthentificationManager().setToken(self._loginToken)
        if characterId:
            PlayerManager().allowAutoConnectCharacter = True
            PlayedCharacterManager().id = characterId
            PlayerManager().autoConnectOfASpecificCharacterId = characterId
        for frame in self._registredInitFrames:
            self._worker.addFrame(frame())
        if self._serverId == 0:
            self._worker.processImmediately(
                LoginValidationWithTokenAction.create(autoSelectServer=False, serverId=self._serverId)
            )
        else:
            self._worker.processImmediately(
                LoginValidationWithTokenAction.create(autoSelectServer=True, serverId=self._serverId)
            )

    def join(self):
        self._joined = True
        while not self._stop.is_set():
            try:
                sleep(1)
                if self.LOG_MEMORY_USAGE:
                    snapshot = tracemalloc.take_snapshot()
                    MemoryProfiler.logMemoryUsage(snapshot)
            except KeyboardInterrupt:
                logger.debug("Shutdown requested by user")
                self.shutdown()
                if self.LOG_MEMORY_USAGE:
                    MemoryProfiler.saveCollectedData()
                sys.exit(0)

        if self._stopReason.reason == DisconnectionReasonEnum.EXCEPTION_THROWN:
            raise Exception(self._stopReason.message)

    def registerInitFrame(self, frame):
        self._registredInitFrames.append(frame)

    def registerGameStartFrame(self, frame):
        self._registredGameStartFrames.append(frame)

    def shutdown(self):
        logger.info("Shuting down ...")
        connh.ConnectionsHandler.connectionGonnaBeClosed(DisconnectionReasonEnum.WANTED_SHUTDOWN)
        connh.ConnectionsHandler.getConnection().close()

    def restart(self):
        conn = connh.ConnectionsHandler.getConnection()
        connh.ConnectionsHandler.connectionGonnaBeClosed(DisconnectionReasonEnum.RESTARTING)
        conn.close()

    def relogin(self):
        self.login(self._loginToken, self._serverId, self._characterId)

    def interrupt(self, reason: DisconnectionReason = None):
        self._stopReason = reason
        self._stop.set()
        if reason and reason.reason == DisconnectionReasonEnum.EXCEPTION_THROWN:
            KernelEventsManager().send(KernelEvts.CRASH, message=reason.message)

    @property
    def exitError(self) -> DisconnectionReason:
        return self._stopReason

    @property
    def mainConn(self) -> "ServerConnection":
        return connh.ConnectionsHandler.getConnection().mainConnection

    @property
    def registeredInitFrames(self) -> list:
        return self._registredInitFrames

    @property
    def registeredGameStartFrames(self) -> list:
        return self._registredGameStartFrames
