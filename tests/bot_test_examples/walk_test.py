import sys

from time import sleep
from com.ankamagames.atouin.managers.FrustumManager import FrustumManager
from com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import (
    WorldPathFinder,
)
from pyd2bot.main import Bot
from com.ankamagames.atouin.messages.MapLoadedMessage import MapLoadedMessage
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.connection.actions.ServerSelectionAction import (
    ServerSelectionAction,
)
from com.ankamagames.dofus.logic.game.approach.actions.CharacterSelectionAction import (
    CharacterSelectionAction,
)
from com.ankamagames.dofus.network.messages.connection.ServersListMessage import (
    ServersListMessage,
)
from com.ankamagames.dofus.network.messages.game.character.choice.CharactersListMessage import (
    CharactersListMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
import threading

logger = Logger(__name__)

newMap = threading.Event()


class MoveNotifFrame(Frame):
    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.LOW

    def pushed(self) -> bool:
        self._worker = Kernel().getWorker()
        return True

    def pulled(self) -> bool:
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, MapComplementaryInformationsDataMessage):
            logger.info("Map loaded")
            newMap.set()


bot = Bot("grinder")
bot._worker.addFrame(MoveNotifFrame())
bot.connect()
bot.mainConn.DEBUG_DATA = True
bot.waitInsideGameMap()
wpf = WorldPathFinder()
wpf.init()
dstMapId = 189792777


def onComputeOver(worldpathfinder: WorldPathFinder, path: list[Edge]):
    if path is None:
        return
    for e in path:
        print(
            e.src.mapId,
            e.dst.mapId,
        )
    for e in path:
        newMap.clear()
        FrustumManager.changeMapToMapdId(e.dst.mapId)
        newMap.wait()


wpf.findPath(dstMapId, onComputeOver)
while True:
    try:
        sleep(0.3)
        if bot.mainConn is None:
            sys.exit(0)
    except KeyboardInterrupt:
        if bot.mainConn is not None:
            bot.mainConn.close()
        sys.exit(0)
