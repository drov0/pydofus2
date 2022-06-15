import sys
import tracemalloc
from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
from time import sleep
import pydofus2.com.ankamagames.dofus.kernel.Kernel as krnl
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import DisconnectionReasonEnum
from pydofus2.com.ankamagames.dofus.logic.connection.actions.LoginValidationWithTokenAction import (
    LoginValidationWithTokenAction,
)
import pydofus2.com.ankamagames.dofus.logic.connection.managers.AuthentificationManager as auth
import pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler as connh
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from pydofus2.com.ankamagames.jerakine.data.I18nFileAccessor import I18nFileAccessor
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from typing import TYPE_CHECKING
from pydofus2.com.ankamagames.jerakine.logger.MemoryProfiler import MemoryProfiler
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.jerakine.network.ServerConnection import ServerConnection
from pydofus2.com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider

logger = Logger("Dofus2")


class DofusClient(metaclass=Singleton):
    LOG_MEMORY_USAGE = False

    def __init__(self):
        krnl.Kernel().init()
        self._worker = krnl.Kernel().getWorker()
        self._registredCustomFrames = []
        I18nFileAccessor().init()
        DataMapProvider().init(AnimatedCharacter)

    def relogin(self):
        self.login(self._loginToken, self._serverId, self._charachterId)

    def login(self, loginToken, serverId=0, charachterId=None):
        if self.LOG_MEMORY_USAGE:
            tracemalloc.start(10)
        self._serverId = serverId
        self._charachterId = charachterId
        self._loginToken = loginToken
        auth.AuthentificationManager().setToken(self._loginToken)
        if charachterId:
            PlayerManager().allowAutoConnectCharacter = True
            PlayedCharacterManager().id = charachterId
            PlayerManager().autoConnectOfASpecificCharacterId = charachterId
        for frame in self._registredCustomFrames:
            self._worker.addFrame(frame)
        if self._serverId == 0:
            self._worker.processImmediately(
                LoginValidationWithTokenAction.create(autoSelectServer=False, serverId=self._serverId)
            )
        else:
            self._worker.processImmediately(
                LoginValidationWithTokenAction.create(autoSelectServer=True, serverId=self._serverId)
            )

    def join(self):
        while True:
            try:
                sleep(1)
                if self.LOG_MEMORY_USAGE:
                    snapshot = tracemalloc.take_snapshot()
                    MemoryProfiler.logMemoryUsage(snapshot)
            except KeyboardInterrupt:
                self.shutdown()
                if self.LOG_MEMORY_USAGE:
                    MemoryProfiler.saveCollectedData()
                sys.exit(0)

    def registerFrame(self, frame):
        self._registredCustomFrames.append(frame)

    def shutdown(self):
        logger.info("Shuting down ...")
        connh.ConnectionsHandler.connectionGonnaBeClosed(DisconnectionReasonEnum.WANTED_SHUTDOWN)
        connh.ConnectionsHandler.getConnection().close()

    def restart(self):
        connh.ConnectionsHandler.connectionGonnaBeClosed(DisconnectionReasonEnum.RESTARTING)
        connh.ConnectionsHandler.getConnection().close()

    @property
    def mainConn(self) -> "ServerConnection":
        return connh.ConnectionsHandler.getConnection().mainConnection
