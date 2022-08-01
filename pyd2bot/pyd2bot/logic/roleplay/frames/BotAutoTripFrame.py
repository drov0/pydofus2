from threading import Timer
from pydofus2.com.DofusClient import DofusClient
from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapInformationsRequestMessage import (
    MapInformationsRequestMessage,
)
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pyd2bot.apis.MoveAPI import MoveAPI
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import (
    WorldPathFinder,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapChangeFailedMessage import (
    MapChangeFailedMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import RoleplayInteractivesFrame
from pyd2bot.logic.roleplay.messages.AutoTripEndedMessage import AutoTripEndedMessage

logger = Logger("Dofus2")


class BotAutoTripFrame(Frame):
    dstMapId = None
    path = None

    def __init__(self, dstMapId: int, rpZone: int = 1):
        self.dstMapId = dstMapId
        self.dstRpZone = rpZone
        self.path = None
        self.changeMapFails = dict()
        self._computed = False
        self._worker = Kernel().getWorker()
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    def reset(self):
        self.dstMapId = None
        self.path = None
        self.changeMapFails.clear()
        self._computed = False

    def pushed(self) -> bool:
        logger.debug("Auto trip frame pushed")
        self._worker = Kernel().getWorker()
        self._computed = False
        self.changeMapFails.clear()
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
            v = WorldPathFinder().currPlayerVertex
            if self.changeMapFails.get(v.UID, 0) > 3:
                DofusClient().restart()
                return True
            if v.UID not in self.changeMapFails:
                self.changeMapFails[v.UID] = 0
            self.changeMapFails[v.UID] += 1
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
        elif self._computed:
            if WorldPathFinder().currPlayerVertex.mapId == self.path[-1].dst.mapId:
                logger.debug("Trip reached destination Map")
                Kernel().getWorker().removeFrame(self)
                Kernel().getWorker().processImmediately(AutoTripEndedMessage(self.dstMapId))
                return True
            logger.debug(f"Current step index: {self.currentEdgeIndex}/{len(self.path)}")
            if self.currentEdgeIndex == len(self.path):
                DofusClient().restart()
            e = self.path[self.currentEdgeIndex]
            logger.debug(f"Moving using next edge")
            print(f"\t|- src {e.src.mapId} -> dst {e.dst.mapId}")
            for tr in e.transitions:
                print(f"\t\t|- direction : {tr.direction}, skill : {tr.skillId}, cell : {tr.cell}")
            MoveAPI.followEdge(e)
        else:
            WorldPathFinder().findPath(self.dstMapId, self.onComputeOver, self.dstRpZone)

    def onComputeOver(self, *args):
        self._computed = True
        path: list[Edge] = None
        for arg in args:
            if isinstance(arg, list):
                path = arg
                break
        if path is None:
            Kernel().getWorker().removeFrame(self)
            Kernel().getWorker().process(AutoTripEndedMessage(None))
            return True
        if len(path) == 0:
            Kernel().getWorker().removeFrame(self)
            Kernel().getWorker().process(AutoTripEndedMessage(self.dstMapId))
            return True
        logger.debug(f"\nPath found: ")
        for e in path:
            print(f"\t|- src {e.src.mapId} -> dst {e.dst.mapId}")
            for tr in e.transitions:
                print(f"\t\t|- direction : {tr.direction}, skill : {tr.skillId}, cell : {tr.cell}")
        self.path: list[Edge] = path
        self.walkToNextStep()
