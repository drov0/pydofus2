import sys
from com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from time import sleep
import com.ankamagames.dofus.kernel.Kernel as krnl
from com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import DisconnectionReasonEnum
from com.ankamagames.dofus.logic.common.frames.MiscFrame import MiscFrame
from com.ankamagames.dofus.logic.connection.actions.LoginValidationWithTokenAction import (
    LoginValidationWithTokenAction,
)
import com.ankamagames.dofus.logic.connection.managers.AuthentificationManager as auth
import com.ankamagames.dofus.kernel.net.ConnectionsHandler as connh
from com.ankamagames.dofus.logic.game.common.frames.InventoryManagementFrame import (
    InventoryManagementFrame,
)
from com.ankamagames.dofus.logic.game.common.frames.JobsFrame import JobsFrame
from com.ankamagames.dofus.logic.game.common.frames.SpellInventoryManagementFrame import (
    SpellInventoryManagementFrame,
)
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
from pyd2bot.frames.BotGameApproachFrame import BotGameApproach
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
        krnl.Kernel().init()
        self._loginToken = Haapi().getLoginToken(self._accountId)
        auth.AuthentificationManager().setToken(self._loginToken)
        self._worker.addFrame(BotGameApproach(self._charachterId))
        self._worker.addFrame(InventoryManagementFrame())
        self._worker.addFrame(SpellInventoryManagementFrame())
        self._worker.addFrame(JobsFrame())
        self._worker.addFrame(MiscFrame())
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
                    self.relogin()
            except KeyboardInterrupt:
                connh.ConnectionsHandler.getConnection().close()
                sys.exit(0)

    def registerFrame(self, frame):
        self._registredCustomFrames.append(frame)

    def restart(self):
        connh.ConnectionsHandler.connectionGonnaBeClosed(DisconnectionReasonEnum.RESTARTING)
        connh.ConnectionsHandler.getConnection().close()

    @property
    def mainConn(self) -> "ServerConnection":
        return connh.ConnectionsHandler.getConnection().mainConnection
