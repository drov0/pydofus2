from threading import Timer
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
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
        return Priority.LOW

    def reset(self):
        self.dstMapId = None
        self.nextStepIndex = None
        self.path = None
        self.changeMapFails = 0
        self._computed = False
        self._worker = Kernel().getWorker()

    def pushed(self) -> bool:
        self._worker = Kernel().getWorker()
        self._computed = False
        self.changeMapFails = 0
        self.nextStepIndex = None
        self.path = None
        self.walkToNextStep()
        return True

    def pulled(self) -> bool:
        self.reset()
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
            Timer(0.1, self.walkToNextStep).start()
            return
        if self.nextStepIndex is not None:
            logger.debug(f"Next step index: {self.nextStepIndex}/{len(self.path)}")
            if self.nextStepIndex == len(self.path):
                Kernel().getWorker().removeFrame(self)
                Kernel().getWorker().process(AutoTripEndedMessage(self.dstMapId))
                return True
            e = self.path[self.nextStepIndex]
            self.nextStepIndex += 1
            direction = DirectionsEnum(e.transitions[0].direction)
            MoveAPI.changeMapToDstDirection(direction)
        else:
            WorldPathFinder().findPath(self.dstMapId, self.onComputeOver)

    def onComputeOver(self, *args):
        path = None
        for arg in args:
            if isinstance(arg, list):
                path = arg
                break
        if path is None:
            raise Exception("No path found")
        if len(path) == 0:
            Kernel().getWorker().process(AutoTripEndedMessage(self.dstMapId))
            return True
        self.path = path
        e = self.path[0]
        direction = DirectionsEnum(e.transitions[0].direction)
        MoveAPI.changeMapToDstDirection(direction)
        self._computed = True
        self.nextStepIndex = 1
