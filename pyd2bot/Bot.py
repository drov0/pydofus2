import sys
from time import sleep
import com.ankamagames.dofus.kernel.Kernel as krnl
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

if TYPE_CHECKING:
    from com.ankamagames.jerakine.network.ServerConnection import ServerConnection
from hackedLauncher.Launcher import Haapi
from pyd2bot.managers.BotsDataManager import BotsDataManager
from pyd2bot.frames.BotGameApproach import BotGameApproach
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider

logger = Logger(__name__)


class Bot:
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
        I18nFileAccessor().init()
        DataMapProvider().init(AnimatedCharacter)
        WorldPathFinder().init()

    def stop(self):
        connh.ConnectionsHandler.getConnection().close()

    def start(self):
        self._worker.processImmediately(
            LoginValidationWithTokenAction.create(
                autoSelectServer=True, serverId=self.SERVER_ID
            )
        )
        while True:
            try:
                sleep(0.2)
                if self.mainConn is None:
                    sys.exit(0)
            except KeyboardInterrupt:
                if self.mainConn is not None:
                    self.mainConn.close()
                sys.exit(0)

    def addFrame(self, frame):
        self._worker.addFrame(frame)

    def registerFrame(self, frame):
        self._worker.addFrame(frame)

    def waitInsideGameMap(self):
        self._gameApproachFrame._insideGame.wait()

    @property
    def mainConn(self) -> "ServerConnection":
        return connh.ConnectionsHandler.getConnection().mainConnection
