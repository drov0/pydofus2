import sys
from time import sleep
from com.ankamagames.dofus import Constants
import com.ankamagames.dofus.kernel.Kernel as krnl
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
from pyd2bot.BotsDataManager import BotsDataManager
from pyd2bot.frames.BotAuthFrame import BotAuthFrame
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from pyd2bot.frames.BotFarmFrame import BotFarmFrame

logger = Logger(__name__)


class Bot:
    AUTH_SERVER_HOST = "54.76.16.121"
    PORT = 5555

    def __init__(self, name):
        self.name = name
        botCreds = BotsDataManager.getEntry(self.name)
        self.SERVER_ID = botCreds["serverId"]
        self.CHARACTER_ID = botCreds["charachterId"]
        self.ACCOUNT_ID = botCreds["account"]
        self.haapi = Haapi()
        self.LOGIN_TOKEN = self.haapi.getLoginToken(self.ACCOUNT_ID)
        auth.AuthentificationManager().setToken(self.LOGIN_TOKEN)
        krnl.Kernel().init()
        self._worker = krnl.Kernel().getWorker()
        self._authFrame = BotAuthFrame(self.SERVER_ID, self.CHARACTER_ID)
        self._worker.addFrame(self._authFrame)
        I18nFileAccessor().init(Constants.LANG_FILE_PATH)
        DataMapProvider().init(AnimatedCharacter)
        WorldPathFinder().init()

    def stop(self):
        connh.ConnectionsHandler.getConnection().close()

    def connect(self):
        connh.ConnectionsHandler.connectToLoginServer(self.AUTH_SERVER_HOST, self.PORT)

    def addFrame(self, frame):
        self._worker.addFrame(frame)

    def waitInsideGameMap(self):
        self._authFrame._insideGame.wait()

    @property
    def mainConn(self) -> "ServerConnection":
        return connh.ConnectionsHandler.getConnection().mainConnection


if __name__ == "__main__":
    botName = sys.argv[1]
    bot = Bot(botName)
    bot.addFrame(BotFarmFrame())
    bot.connect()
    while True:
        try:
            sleep(0.3)
            if bot.mainConn is None:
                sys.exit(0)
        except KeyboardInterrupt:
            if bot.mainConn is not None:
                bot.mainConn.close()
            sys.exit(0)
