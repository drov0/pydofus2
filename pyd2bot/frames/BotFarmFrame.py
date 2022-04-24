import threading
from com.ankamagames.atouin.managers.FrustumManager import FrustumManager
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseEndedMessage import (
    InteractiveUseEndedMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseErrorMessage import (
    InteractiveUseErrorMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUsedMessage import (
    InteractiveUsedMessage,
)
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import (
        RoleplayInteractivesFrame,
    )
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import (
        RoleplayEntitiesFrame,
    )
logger = Logger(__name__)


class BotFarmFrame(Frame):
    def __init__(self):
        super().__init__()
        self.nbrOfFails = 0
        self._currentRequestedElementId = -1
        self._usingInteractive = False
        self._entities = dict()

    @property
    def priority(self) -> int:
        return Priority.LOW

    @property
    def rolePlayEntitiesFrame(self) -> "RoleplayEntitiesFrame":
        return Kernel().getWorker().getFrame("RoleplayEntitiesFrame")

    @property
    def roleplayInteractivesFrame(self) -> "RoleplayInteractivesFrame":
        return Kernel().getWorker().getFrame("RoleplayInteractivesFrame")

    def pushed(self) -> bool:
        self._worker = Kernel().getWorker()
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, InteractiveUseErrorMessage):
            if self.nbrOfFails > 3:
                raise Exception("Too many fails, aborting")
            if msg.elemId == self._currentRequestedElementId:
                self._currentRequestedElementId = -1
                self._usingInteractive = False
                self.nbrOfFails += 1
                if not self.collectResource():
                    FrustumManager.randomMapChange()
            return True

        if isinstance(msg, InteractiveUsedMessage):
            self.nbrOfFails = 0
            if PlayedCharacterManager().id == msg.entityId and msg.duration > 0:
                self._currentUsedElementId = msg.elemId
            if self._currentRequestedElementId == msg.elemId:
                self._currentRequestedElementId = -1
            if msg.duration > 0:
                if PlayedCharacterManager().id == msg.entityId:
                    self._usingInteractive = True
            self._entities[msg.elemId] = msg.entityId
            return True

        if isinstance(msg, InteractiveUseEndedMessage):
            if self._entities[msg.elemId] == PlayedCharacterManager().id:
                self._usingInteractive = False
                self._currentUsedElementId = -1
                if not self.collectResource():
                    FrustumManager.randomMapChange()
            del self._entities[msg.elemId]
            return True

        if isinstance(msg, MapComplementaryInformationsDataMessage):
            if not self.collectResource():
                FrustumManager.randomMapChange()

    def collectResource(self):
        for ie in self.rolePlayEntitiesFrame.interactiveElements:
            ie_data = self.roleplayInteractivesFrame.getInteractiveElement(ie.elementId)
            interactiveSkill = self.roleplayInteractivesFrame.canBeCollected(
                ie.elementId
            )
            if interactiveSkill is not None:
                self.roleplayInteractivesFrame.skillClicked(
                    ie_data, interactiveSkill.skillInstanceUid
                )
                self._currentRequestedElementId = ie.elementId
                return True
        return False
