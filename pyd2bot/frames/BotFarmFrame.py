from email.errors import FirstHeaderLineIsContinuationDefect
import threading
from com.ankamagames.atouin.managers.FrustumManager import FrustumManager
from com.ankamagames.dofus.datacenter.jobs.Skill import Skill
from com.ankamagames.dofus.datacenter.notifications.Notification import Notification
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.network.messages.game.context.notification.NotificationByServerMessage import (
    NotificationByServerMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveElementUpdatedMessage import (
    InteractiveElementUpdatedMessage,
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
from com.ankamagames.dofus.network.messages.game.interactive.StatedElementUpdatedMessage import (
    StatedElementUpdatedMessage,
)
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from typing import TYPE_CHECKING

from pyd2bot.apis.FarmAPI import FarmAPI

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
        self.discard = []
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
            if msg.elemId == self._currentRequestedElementId:
                logger.error(
                    f"[BotFarmFrame] Error unable to use interactive element {msg.elemId} with the skill {msg.skillInstanceUid}"
                )
                self._usingInteractive = False
                self.discard.append(msg.elemId)
                self._currentRequestedElementId = FarmAPI().collectResource()
                if self._currentRequestedElementId == -1:
                    FrustumManager.randomMapChange()
            return True

        if isinstance(msg, InteractiveUsedMessage):
            self.nbrOfFails = 0
            if PlayedCharacterManager().id == msg.entityId and msg.duration > 0:
                logger.debug(
                    f"[BotFarmFrame] Started using interactive element {msg.elemId} ...."
                )
                self._currentRequestedElementId = msg.elemId
            if self._currentRequestedElementId == msg.elemId:
                self._currentRequestedElementId = -1
            if msg.duration > 0:
                if PlayedCharacterManager().id == msg.entityId:
                    self._usingInteractive = True
            self._entities[msg.elemId] = msg.entityId
            return True

        if isinstance(msg, InteractiveUseEndedMessage):
            if self._entities[msg.elemId] == PlayedCharacterManager().id:
                logger.debug(
                    f"[BotFarmFrame] Interactive element {msg.elemId} use ended"
                )
                self._usingInteractive = FirstHeaderLineIsContinuationDefect
                self.lastCollected = msg.elemId
                self._currentRequestedElementId = FarmAPI().collectResource()
                if self._currentRequestedElementId == -1:
                    FrustumManager.randomMapChange()
            del self._entities[msg.elemId]
            return True

        if isinstance(msg, MapComplementaryInformationsDataMessage):
            self.discard.clear()
            self._currentRequestedElementId = FarmAPI().collectResource()
            if self._currentRequestedElementId == -1:
                FrustumManager.randomMapChange()

        if isinstance(msg, NotificationByServerMessage):
            notification = Notification.getNotificationById(msg.id)
            if notification.titleId == 756273:
                # inventory full notification
                raise Exception(f"[{notification.title}] {notification.message}")
