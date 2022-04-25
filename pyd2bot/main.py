import signal
import sys
from time import perf_counter, sleep
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
from hackedLauncher.Launcher import Haapi
from pyd2bot.BotsDataManager import BotsDataManager
from pyd2bot.frames.BotAuthFrame import BotAuthFrame
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from pyd2bot.frames.BotFarmFrame import BotFarmFrame

logger = Logger(__name__)


class TestBot:
    AUTH_SERVER = "54.76.16.121"
    PORT = 5555
    CONN = {
        "host": AUTH_SERVER,
        "port": PORT,
    }

    def __init__(self, name):
        self.name = name
        botInfos = BotsDataManager.getEntry(self.name)
        self.SERVER_ID = botInfos["serverId"]
        self.CHARACTER_ID = botInfos["charachterId"]
        self.ACCOUNT_ID = botInfos["account"]
        self.haapi = Haapi()
        self.TOKEN = self.haapi.getLoginToken(self.ACCOUNT_ID)
        I18nFileAccessor().init(Constants.LANG_FILE_PATH)
        DataMapProvider().init(AnimatedCharacter)
        WorldPathFinder().init()

    def stop(self):
        connh.ConnectionsHandler.getConnection().close()

    def main(self):
        krnl.Kernel().init()
        krnl.Kernel().getWorker().addFrame(
            BotAuthFrame(self.SERVER_ID, self.CHARACTER_ID)
        )
        krnl.Kernel().getWorker().addFrame(BotFarmFrame())
        auth.AuthentificationManager().setToken(self.TOKEN)
        connh.ConnectionsHandler.connectToLoginServer(**self.CONN)

    @property
    def mainConn(self):
        return connh.ConnectionsHandler.getConnection().mainConnection


if __name__ == "__main__":
    botName = sys.argv[1]
    bot = TestBot(botName)
    bot.main()
    while True:
        try:
            sleep(0.3)
        except KeyboardInterrupt:
            bot.mainConn.close()
            sys.exit(0)
