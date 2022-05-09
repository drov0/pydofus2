import sys
from com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
from time import sleep
import com.ankamagames.dofus.kernel.Kernel as krnl
from com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import DisconnectionReasonEnum
from com.ankamagames.dofus.logic.connection.actions.LoginValidationWithTokenAction import (
    LoginValidationWithTokenAction,
)
import com.ankamagames.dofus.logic.connection.managers.AuthentificationManager as auth
import com.ankamagames.dofus.kernel.net.ConnectionsHandler as connh
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import (
    WorldPathFinder,
)
from com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from com.ankamagames.jerakine.data.I18nFileAccessor import I18nFileAccessor
from com.ankamagames.jerakine.logger.Logger import Logger
from typing import TYPE_CHECKING

from com.ankamagames.jerakine.metaclasses.Singleton import Singleton

if TYPE_CHECKING:
    from com.ankamagames.jerakine.network.ServerConnection import ServerConnection
from launcher.Launcher import Haapi
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider

logger = Logger("Dofus2")


class DofusClient(metaclass=Singleton):
    def __init__(self):
        krnl.Kernel().init()
        self._worker = krnl.Kernel().getWorker()
        self._registredCustomFrames = []
        I18nFileAccessor().init()
        DataMapProvider().init(AnimatedCharacter)
        WorldPathFinder().init()

    def relogin(self):
        self.login(self._accountId, self._serverId, self._charachterId)

    def login(self, accountId, serverId, charachterId):
        self._serverId = serverId
        self._charachterId = charachterId
        self._accountId = accountId
        self._loginToken = Haapi().getLoginToken(self._accountId)
        auth.AuthentificationManager().setToken(self._loginToken)
        PlayerManager().allowAutoConnectCharacter = True
        PlayerManager().autoConnectOfASpecificCharacterId = charachterId
        for frame in self._registredCustomFrames:
            self._worker.addFrame(frame)
        self._worker.processImmediately(
            LoginValidationWithTokenAction.create(autoSelectServer=True, serverId=self._serverId)
        )

    def join(self):
        while True:
            try:
                sleep(0.3)
                if not self.mainConn:
                    sys.exit(0)
            except KeyboardInterrupt:
                self.shutdown()
                sys.exit(0)

    def registerFrame(self, frame):
        self._registredCustomFrames.append(frame)

    def shutdown(self):
        connh.ConnectionsHandler.connectionGonnaBeClosed(DisconnectionReasonEnum.WANTED_SHUTDOWN)
        connh.ConnectionsHandler.getConnection().close()

    def restart(self):
        connh.ConnectionsHandler.connectionGonnaBeClosed(DisconnectionReasonEnum.RESTARTING)
        connh.ConnectionsHandler.getConnection().close()

    @property
    def mainConn(self) -> "ServerConnection":
        return connh.ConnectionsHandler.getConnection().mainConnection