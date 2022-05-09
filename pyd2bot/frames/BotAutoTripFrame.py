from cmath import log
from threading import Timer
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapInformationsRequestMessage import (
    MapInformationsRequestMessage,
)
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from pyd2bot.apis.MoveAPI import MoveAPI
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import (
    WorldPathFinder,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapChangeFailedMessage import (
    MapChangeFailedMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.types.enums.DirectionsEnum import DirectionsEnum
from com.ankamagames.jerakine.types.enums.Priority import Priority
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import RoleplayInteractivesFrame

from pyd2bot.messages.AutoTripEndedMessage import AutoTripEndedMessage

logger = Logger("Dofus2")


class BotAutoTripFrame(Frame):
    dstMapId = None
    path = None

    def __init__(self, dstMapId):
        self.dstMapId = dstMapId
        self.path = None
        self.changeMapFails = 0
        self._computed = False
        self._worker = Kernel().getWorker()
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    def reset(self):
        self.dstMapId = None
        self.path = None
        self.changeMapFails = 0
        self._computed = False

    def pushed(self) -> bool:
        logger.debug("Auto trip frame pushed")
        self._worker = Kernel().getWorker()
        self._computed = False
        self.changeMapFails = 0
        self.path = None
        Timer(0.2, self.walkToNextStep).start()
        return True

    def pulled(self) -> bool:
        self.reset()
        logger.debug("Auto trip frame pulled")
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, MapComplementaryInformationsDataMessage):
            if self._computed:
                self.walkToNextStep()
            return True

        if isinstance(msg, MapChangeFailedMessage):
            mirmsg = MapInformationsRequestMessage()
            mirmsg.init(mapId_=MapDisplayManager().currentMapPoint.mapId)
            ConnectionsHandler.getConnection().send(mirmsg)
            return True

    @property
    def currentEdgeIndex(self):
        v = WorldPathFinder().currPlayerVertex
        i = 0
        while i < len(self.path):
            if self.path[i].src == v:
                break
            i += 1
        return i

    def walkToNextStep(self):
        if not PlayedCharacterManager().currentMap:
            Timer(0.1, self.walkToNextStep).start()
            return
        if PlayedCharacterManager().currentMap.mapId == self.dstMapId:
            logger.debug("Trip reached destination Map")
            Kernel().getWorker().removeFrame(self)
            Kernel().getWorker().processImmediately(AutoTripEndedMessage(self.dstMapId))
            return True
        elif self._computed:
            logger.debug(f"Current step index: {self.currentEdgeIndex}/{len(self.path)}")
            if self.currentEdgeIndex == len(self.path):
                raise Exception("Unexpected behavior: asking to move beyond path should have returned before")
            MoveAPI.followEdge(self.path[self.currentEdgeIndex])
        else:
            WorldPathFinder().findPath(self.dstMapId, self.onComputeOver)

    def onComputeOver(self, *args):
        self._computed = True
        path: list[Edge] = None
        for arg in args:
            if isinstance(arg, list):
                path = arg
                break
        if len(path) == 0:
            raise Exception("Unexpected behavior: path is empty")
        if path is None:
            Kernel().getWorker().removeFrame(self)
            Kernel().getWorker().process(AutoTripEndedMessage(None))
            return True
        logger.debug(f"\nPath found: ")
        for e in path:
            print(f"\t|- src {e.src.mapId} -> dst {e.dst.mapId}")
            for tr in e.transitions:
                print(f"\t\t|- direction : {tr.direction}, skill : {tr.skillId}, cell : {tr.cell}")
        self.path: list[Edge] = path
        self.walkToNextStep()
