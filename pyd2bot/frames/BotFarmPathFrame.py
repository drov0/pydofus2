from email.errors import FirstHeaderLineIsContinuationDefect
from threading import Timer
from time import sleep
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.InventoryManager import (
    InventoryManager,
)
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.messages.FightRequestFailed import FightRequestFailed
from com.ankamagames.dofus.logic.game.fight.messages.MapMoveFailed import MapMoveFailed
from com.ankamagames.dofus.logic.game.roleplay.actions.DeleteObjectAction import (
    DeleteObjectAction,
)
from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame
from com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayGroupMonsterInformations import (
    GameRolePlayGroupMonsterInformations,
)
from pyd2bot.DofusClient import DofusClient
from pyd2bot.apis.InventoryAPI import InventoryAPI
from pyd2bot.apis.MoveAPI import MoveAPI
from com.ankamagames.dofus.datacenter.notifications.Notification import Notification
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.network.messages.game.context.notification.NotificationByServerMessage import (
    NotificationByServerMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapChangeFailedMessage import (
    MapChangeFailedMessage,
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
from typing import TYPE_CHECKING, Tuple

from pyd2bot.apis.FarmAPI import FarmAPI
from pyd2bot.frames.BotAutoTripFrame import BotAutoTripFrame
from pyd2bot.models.FarmParcours import FarmParcours

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import (
        RoleplayInteractivesFrame,
    )
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import (
        RoleplayEntitiesFrame,
    )
logger = Logger(__name__)


def GetNextMap(path, index):
    return path[index]


class BotFarmPathFrame(Frame):
    def __init__(self, parcours: FarmParcours):
        super().__init__()
        self._followingIe = -1
        self._usingInteractive = False
        self._wantmapChange = -1
        self._entities = dict()
        self.parcours = parcours
        self._inAutoTrip = False
        self.pathIndex = None
        self.lastGoodCellId = None
        self._worker = Kernel().getWorker()

    @property
    def currMapCoords(self):
        mp = MapPosition.getMapPositionById(MapDisplayManager().dataMap.id)
        return mp.posX, mp.posY

    @property
    def priority(self) -> int:
        return Priority.LOW

    @property
    def entitiesFrame(self) -> "RoleplayEntitiesFrame":
        return Kernel().getWorker().getFrame("RoleplayEntitiesFrame")

    @property
    def interactivesFrame(self) -> "RoleplayInteractivesFrame":
        return Kernel().getWorker().getFrame("RoleplayInteractivesFrame")

    @property
    def movementFrame(self) -> "RoleplayMovementFrame":
        return Kernel().getWorker().getFrame("RoleplayMovementFrame")

    @property
    def nextPathMapCoords(self):
        if self.currMapCoords in self.parcours.path:
            index = (self.parcours.path.index(self.currMapCoords) + 1) % len(self.parcours.path)
            return self.parcours.path[index]
        return None

    def pushed(self) -> bool:
        self.reset()
        return True

    def pulled(self) -> bool:
        return self.reset()

    def reset(self):
        self._discardedMonsters = set()
        self._wantmapChange = -1
        self._followingIe = -1
        self._usingInteractive = False
        self._followinMonsterGroup = None
        self._lastCellId = None
        if self.movementFrame:
            self.movementFrame._canMove = True
            self.movementFrame._followingMonsterGroup = None
            self.movementFrame._followingIe = None
            self.movementFrame._isRequestingMovement = False
            self.movementFrame._wantToChangeMap = None
            if self.movementFrame._requestFightTimeout:
                self.movementFrame._requestFightTimeout.cancel()
            self.movementFrame._requestFighFails = 0
            if self.movementFrame._changeMapTimeout:
                self.movementFrame._changeMapTimeout.cancel()
        if self.interactivesFrame:
            self.interactivesFrame.currentRequestedElementId = None
            self.interactivesFrame.usingInteractive = False

    def process(self, msg: Message) -> bool:

        if PlayedCharacterManager().isFighting:
            return False
        if Kernel().getWorker().contains("BotAutoTripFrame"):
            logger.debug("BotAutoTripFrame is running, aborting")
            return False

        if isinstance(msg, InteractiveUseErrorMessage):
            logger.error(
                f"[BotFarmFrame] Error unable to use interactive element {msg.elemId} with the skill {msg.skillInstanceUid}"
            )
            logger.debug("***********************************************************************")
            if msg.elemId == self._followingIe:
                self.reset()
                logger.debug("Will move on")
                del self.interactivesFrame._ie[msg.elemId]
                del self.interactivesFrame._collectableIe[msg.elemId]
                self.reset()
                self.doFarm()
            return True

        elif isinstance(msg, (FightRequestFailed, MapChangeFailedMessage, MapMoveFailed)):
            logger.error(f"Fatal error, restarting bot")
            self.reset()
            DofusClient().restart()

        elif isinstance(msg, InteractiveUsedMessage):
            if PlayedCharacterManager().id == msg.entityId and msg.duration > 0:
                logger.debug(f"[BotFarmFrame] Inventory weight {InventoryAPI.getWeightPercent():.2f}%")
                logger.debug(f"[BotFarmFrame] Started using interactive element {msg.elemId} ....")
                if self._followingIe == msg.elemId:
                    self._followingIe = -1
                if msg.duration > 0:
                    self._usingInteractive = True
            self._entities[msg.elemId] = msg.entityId
            return True

        elif isinstance(msg, InteractiveUseEndedMessage):
            if self._entities[msg.elemId] == PlayedCharacterManager().id:
                logger.debug(f"[BotFarmFrame] Interactive element {msg.elemId} use ended")
                logger.debug("*" * 100)
                self.reset()
                self.doFarm()
            del self._entities[msg.elemId]
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            sleep(0.2)
            self._discardedMonsters.clear()
            logger.debug("-" * 100)
            if self.currMapCoords not in self.parcours.path:
                logger.debug(f"[BotFarmFrame] Map {self.currMapCoords} not in path will add autotripFrame")
                self._worker.addFrame(BotAutoTripFrame(self.parcours.startMapId))
                return False
            else:
                self.reset()
                self.doFarm()
                return True

        elif isinstance(msg, NotificationByServerMessage):
            notification = Notification.getNotificationById(msg.id)
            if notification.titleId == 756273:
                logger.debug("[BotFarmFrame] Full pod reached will destroy all items in inventory")
                InventoryAPI.destroyAllItems()
                self.doFarm()
            return True

    def moveToNextStep(self):
        x, y = self.nextPathMapCoords
        logger.debug(f"[BotFarmFrame] Current Map {self.currMapCoords} Moving to {x, y}")
        self._wantmapChange = MoveAPI.changeMapToDstCoords(x, y)
        if self._wantmapChange == -1:
            raise Exception(f"Unable to move to Map {x, y}")
        self._changeMapTimeout = Timer(5, self.moveToNextStep)

    def doFight(self):
        for entityId in self.entitiesFrame._monstersIds:
            if entityId not in self._discardedMonsters:
                infos: GameRolePlayGroupMonsterInformations = self.entitiesFrame.getEntityInfos(entityId)
                if infos.staticInfos.mainCreatureLightInfos.level <= PlayedCharacterManager().limitedLevel:
                    self.movementFrame.attackMonsters(entityId)
                    return entityId
        return None

    def doFarm(self):
        if InventoryAPI.getWeightPercent() > 90:
            InventoryAPI.destroyAllItems()
        self._lastCellId = PlayedCharacterManager().currentCellId
        if self.parcours.fightOnly:
            self._followinMonsterGroup = self.doFight()
        else:
            self._followingIe = FarmAPI().collectResource(skills=self.parcours.skills)
        if self._followingIe == -1 and self._followinMonsterGroup is None:
            self.moveToNextStep()
