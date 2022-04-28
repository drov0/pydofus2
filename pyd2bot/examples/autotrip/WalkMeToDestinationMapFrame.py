from mailbox import Message
from tkinter import Frame
from pyd2bot.apis.MoveAPI import MoveAPI
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge
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

logger = Logger(__name__)


class WalkMeToDestinationMapFrame(Frame):
    dstMapId = None
    nextStepIndex = None
    path = None

    def __init__(self, dstmapid):
        self.dstMapId = dstmapid
        self.nextStepIndex = None
        self.path = None
        self.changeMapFails = 0
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
            logger.debug("Next step index: %s", self.nextStepIndex)
            if self.nextStepIndex is not None:
                if self.nextStepIndex == len(self.path):
                    logger.info("Arrived at destination")
                    return True
                e = self.path[self.nextStepIndex]
                self.nextStepIndex += 1
                direction = DirectionsEnum(e.transitions[0].direction)
                MoveAPI.changeMapToDirection(direction)
            else:
                WorldPathFinder().findPath(self.dstMapId, self.onComputeOver)

        if isinstance(msg, MapChangeFailedMessage):
            if self.changeMapFails > 5:
                logger.error("Too many map change fails")
                return True
            self.changeMapFails += 1
            Kernel().getWorker().getFrame("RoleplayMovementFrame").askMapChange()

    def onComputeOver(self, *args):
        path = None
        for arg in args:
            if isinstance(arg, list):
                path = arg
                break
        if path is None:
            raise Exception("No path found")
        if len(path) == 0:
            logger.info("Already at destination")
            return True
        self.path = path
        e = self.path[0]
        self.nextStepIndex = 1
        direction = DirectionsEnum(e.transitions[0].direction)
        MoveAPI.changeMapToDirection(direction)
