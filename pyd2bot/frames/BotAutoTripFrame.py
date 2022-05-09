from threading import Timer
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge
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
    nextStepIndex = None
    path = None

    def __init__(self, dstmapid):
        self.dstMapId = dstmapid
        self.nextStepIndex = None
        self.path = None
        self.changeMapFails = 0
        self._computed = False
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    def reset(self):
        self.dstMapId = None
        self.nextStepIndex = None
        self.path = None
        self.changeMapFails = 0
        self._computed = False
        self._worker = Kernel().getWorker()

    def pushed(self) -> bool:
        logger.debug("Auto trip frame pushed")
        self._worker = Kernel().getWorker()
        self._computed = False
        self.changeMapFails = 0
        self.nextStepIndex = None
        self.path = None
        Timer(0.2, self.walkToNextStep).start()
        return True

    def pulled(self) -> bool:
        self.reset()
        logger.debug("Auto trip frame pulled")
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, MapComplementaryInformationsDataMessage):
            logger.debug(f"New map entered")
            if self._computed:
                self.walkToNextStep()
            return True

        if isinstance(msg, MapChangeFailedMessage):
            if self.changeMapFails > 5:
                logger.error("Too many map change fails")
                return True
            self.changeMapFails += 1
            rolePlayFrame: "RoleplayMovementFrame" = Kernel().getWorker().getFrame("RoleplayMovementFrame")
            rolePlayFrame.askMapChange()
        return True

    def walkToNextStep(self):
        if not DofusEntities.getEntity(PlayedCharacterManager().id):
            logger.error("Player not found")
            Timer(5, self.walkToNextStep).start()
            return
        if self.nextStepIndex is not None:
            logger.debug(f"Next step index: {self.nextStepIndex}/{len(self.path)}")
            if self.nextStepIndex == len(self.path):
                logger.debug("Trip reached destination map")
                Kernel().getWorker().removeFrame(self)
                Kernel().getWorker().processImmediately(AutoTripEndedMessage(self.dstMapId))
                return True
            e = self.path[self.nextStepIndex]
            self.nextStepIndex += 1
            MoveAPI.followEdge(e)
        else:
            WorldPathFinder().findPath(self.dstMapId, self.onComputeOver)

    def onComputeOver(self, *args):
        path: list[Edge] = None
        for arg in args:
            if isinstance(arg, list):
                path = arg
                break
        if path is None or len(path) == 0:
            logger.error("No path found")
            Kernel().getWorker().removeFrame(self)
            Kernel().getWorker().process(AutoTripEndedMessage(None))
            return True
        logger.debug(f"Path found: ")
        for e in path:
            print(f"/t * src {e.src.mapId} -> dst {e.dst.mapId}")
            for tr in e.transitions:
                print(f"/t/t - direction : {tr.direction}, skill : {tr.skillId}, cell : {tr.cell}")
        self.path: list[Edge] = path
        MoveAPI.followEdge(self.path[0])
        self._computed = True
        self.nextStepIndex = 1
