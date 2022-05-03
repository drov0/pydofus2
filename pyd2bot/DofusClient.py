import sys
from time import sleep
import com.ankamagames.dofus.kernel.Kernel as krnl
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

if TYPE_CHECKING:
    from com.ankamagames.jerakine.network.ServerConnection import ServerConnection
from launcher.Launcher import Haapi
from pyd2bot.managers.BotsDataManager import BotsDataManager
from pyd2bot.frames.BotGameApproachFrame import BotGameApproach
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider

logger = Logger(__name__)


class DofusClient:
    def __init__(self, name):
        self.name = name
        botCreds = BotsDataManager.getEntry(self.name)
        self.SERVER_ID = botCreds["serverId"]
        self.CHARACTER_ID = botCreds["charachterId"]
        self.ACCOUNT_ID = botCreds["account"]
        self.LOGIN_TOKEN = Haapi().getLoginToken(self.ACCOUNT_ID)
        auth.AuthentificationManager().setToken(self.LOGIN_TOKEN)
        krnl.Kernel().init()
        self._worker = krnl.Kernel().getWorker()
        self._gameApproachFrame = BotGameApproach(self.CHARACTER_ID)
        self._worker.addFrame(self._gameApproachFrame)
        self._worker.addFrame(InventoryManagementFrame())
        self._worker.addFrame(SpellInventoryManagementFrame())
        self._worker.addFrame(JobsFrame())
        self._worker.addFrame(MiscFrame())
        I18nFileAccessor().init()
        DataMapProvider().init(AnimatedCharacter)
        WorldPathFinder().init()

    def stop(self):
        connh.ConnectionsHandler.getConnection().close()

    def connect(self):
        self._worker.processImmediately(
            LoginValidationWithTokenAction.create(autoSelectServer=True, serverId=self.SERVER_ID)
        )

    def join(self):
        while True:
            try:
                sleep(0.2)
                if self.mainConn is None:
                    sys.exit(0)
            except KeyboardInterrupt:
                try:
                    if self.mainConn is not None:
                        self.mainConn.close()
                except Exception:
                    pass
                sys.exit(0)

    def start(self):
        self.connect()

    def registerFrame(self, frame):
        self._worker.addFrame(frame)

    def waitInsideGameMap(self):
        self._gameApproachFrame._insideGame.wait()

    @property
    def mainConn(self) -> "ServerConnection":
        return connh.ConnectionsHandler.getConnection().mainConnection
