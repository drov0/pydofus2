import signal
import sys
from time import perf_counter, sleep
from com.ankamagames.atouin.managers.FrustumManager import FrustumManager
from com.ankamagames.dofus import Constants
import com.ankamagames.dofus.kernel.Kernel as krnl
from com.ankamagames.dofus.logic.connection.actions.ServerSelectionAction import (
    ServerSelectionAction,
)
import com.ankamagames.dofus.logic.connection.managers.AuthentificationManager as auth
import com.ankamagames.dofus.kernel.net.ConnectionsHandler as connh
from com.ankamagames.dofus.logic.game.approach.actions.CharacterSelectionAction import (
    CharacterSelectionAction,
)
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import (
    WorldPathFinder,
)
from com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from com.ankamagames.jerakine.data.I18nFileAccessor import I18nFileAccessor
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.resources.events.ResourceLoadedEvent import (
    ResourceLoadedEvent,
)

from hackedLauncher.Launcher import Haapi
from pyd2bot.BotsDataManager import BotsDataManager
from pyd2bot.events.BotEventsManager import BotEventsManager
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from pyd2bot.FarmAPI import farmAPI

logger = Logger(__name__)


class TestBot:
    AUTH_SERVER = "54.76.16.121"
    PORT = 5555
    CONN = {
        "host": AUTH_SERVER,
        "port": PORT,
    }

    def __init__(self, name):
        # Load language file to be able to translate ids to actual text
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
        print("Want to stop")
        connh.ConnectionsHandler.getConnection().close()

    def main(self):
        krnl.Kernel().init()
        auth.AuthentificationManager().setToken(self.TOKEN)
        connh.ConnectionsHandler.connectToLoginServer(**self.CONN)
        BotEventsManager().add_listener(
            BotEventsManager.SERVER_SELECTION, self.onServerSelection
        )
        BotEventsManager().add_listener(
            BotEventsManager.CHARACTER_SELECTION, self.onCharacterSelection
        )
        BotEventsManager().add_listener(
            BotEventsManager.SERVER_SELECTED, self.onServerSelectionSuccess
        )
        BotEventsManager().add_listener(
            BotEventsManager.CHARACTER_SELECTED, self.onCharacterSelectionSuccess
        )
        BotEventsManager().add_listener(
            BotEventsManager.SWITCH_TO_ROLEPLAY, self.onRolePlayContextEntred
        )
        BotEventsManager().add_listener(
            BotEventsManager.SWITCH_TO_FIGHT, self.onRolePlayContextEntred
        )
        BotEventsManager().add_listener(
            BotEventsManager.MAP_DATA_LOADED, self.onMapComplementaryDataLoaded
        )

    def onServerSelection(self, event):
        krnl.Kernel().getWorker().process(
            ServerSelectionAction.create(serverId=self.SERVER_ID)
        )

    def onCharacterSelection(self, event):
        krnl.Kernel().getWorker().process(
            CharacterSelectionAction.create(
                characterId=self.CHARACTER_ID, btutoriel=False
            )
        )

    def onServerSelectionSuccess(self, event):
        logger.info("Server selected")

    def onCharacterSelectionSuccess(self, event):
        logger.info("Character selected")

    def onRolePlayContextEntred(self, event):
        logger.info("RolePlay context entered")
        pass

    def onGameFightContextEntered(self, event):
        logger.info("Fight context entered")
        pass

    def onMapComplementaryDataLoaded(self, e: ResourceLoadedEvent):
        logger.info(
            f"Bot is currently in the map {PlayedCharacterManager().currentMap.mapId}"
        )
        FarmAPI.collectRessources()
        FrustumManager.randomMapChange()


if __name__ == "__main__":
    botName = sys.argv[1]
    bot = TestBot(botName)
    bot.main()
    sleep(30)
    socket = connh.ConnectionsHandler.getConnection().mainConnection._socket
    record = socket.recording
    record.position = 0
    with open("recording.bin", "wb") as f:
        f.write(record)
    connh.ConnectionsHandler.getConnection().mainConnection._socket.close()
