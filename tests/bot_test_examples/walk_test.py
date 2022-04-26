import sys

from time import sleep
from com.ankamagames.atouin.managers.FrustumManager import FrustumManager
from com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import (
    WorldPathFinder,
)
from com.ankamagames.jerakine.types.enums.DirectionsEnum import DirectionsEnum
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


class MoveToSameMap(Frame):
    dstMapId = None
    nextStepIndex = None
    path = None
    wpf = None

    def __init__(self, dstmapid):
        self.dstMapId = dstmapid
        self.nextStepIndex = None
        self.path = None
        self.wpf = WorldPathFinder()
        self.wpf.init()

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
            logger.debug("Next step index: %s", MoveToSameMap.nextStepIndex)
            if MoveToSameMap.nextStepIndex is not None:
                if MoveToSameMap.nextStepIndex == len(MoveToSameMap.path):
                    logger.info("Arrived at destination")
                    return True
                e = MoveToSameMap.path[MoveToSameMap.nextStepIndex]
                MoveToSameMap.nextStepIndex += 1
                direction = DirectionsEnum(e.transitions[0].direction)
                FrustumManager.changeMapToDirection(direction)
            else:
                self.wpf.findPath(self.dstMapId, self.onComputeOver)

    @staticmethod
    def onComputeOver(worldpathfinder: WorldPathFinder, path: list[Edge]):
        if path is None:
            return
        MoveToSameMap.path = path
        e = MoveToSameMap.path[0]
        MoveToSameMap.nextStepIndex = 1
        direction = DirectionsEnum(e.transitions[0].direction)
        FrustumManager.changeMapToDirection(direction)


bot = Bot("grinder")
bot._worker.addFrame(MoveToSameMap(189792777))
bot.connect()
bot.mainConn.DEBUG_DATA = True
bot.waitInsideGameMap()


while True:
    try:
        sleep(0.3)
        if bot.mainConn is None:
            sys.exit(0)
    except KeyboardInterrupt:
        if bot.mainConn is not None:
            bot.mainConn.close()
        sys.exit(0)
