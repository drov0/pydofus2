from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapInformationsRequestMessage import (
    MapInformationsRequestMessage,
)
from com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from time import sleep
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition
from com.ankamagames.dofus.logic.game.fight.messages.FightRequestFailed import FightRequestFailed
from com.ankamagames.dofus.logic.game.fight.messages.MapMoveFailed import MapMoveFailed
from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame
from com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayGroupMonsterInformations import (
    GameRolePlayGroupMonsterInformations,
)
from com.DofusClient import DofusClient
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
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
from typing import TYPE_CHECKING

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
logger = Logger("Dofus2")


def GetNextMap(path, index):
    return path[index]


class BotFarmPathFrame(Frame):
    parcours: FarmParcours = None

    def __init__(self, autoStart: bool = False):
        if not BotFarmPathFrame.parcours:
            raise Exception("No parcours loaded")
        super().__init__()
        self._autoStart = autoStart
        self._followingIe = -1
        self._usingInteractive = False
        self._wantmapChange = -1
        self._entities = dict()
        self._inAutoTrip = False
        self._discardedMonstersIds = []
        self._worker = Kernel().getWorker()

    @property
    def currMapCoords(self):
        mp = MapPosition.getMapPositionById(MapDisplayManager().dataMap.id)
        return mp.posX, mp.posY

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

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
        if self._autoStart:
            self.doFarm()
        return True

    def pulled(self) -> bool:
        self.reset()
        return True

    def reset(self):
        self._wantmapChange = -1
        self._followingIe = -1
        self._usingInteractive = False
        self._followinMonsterGroup = None
        self._lastCellId = None
        self._inAutoTrip = False
        self._discardedMonstersIds.clear()
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
            raise Exception("Can't farm while fighting")

        if Kernel().getWorker().contains("BotAutoTripFrame"):
            raise Exception("Can't farm while in auto trip")

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
                self.doFarm()
            return True

        elif isinstance(msg, FightRequestFailed):
            logger.debug(f"[BotFarmFrame] Fight request failed, will dicard the {msg.actorId}")
            self._discardedMonstersIds.append(msg.actorId)
            mirmsg = MapInformationsRequestMessage()
            mirmsg.init(mapId_=MapDisplayManager().currentMapPoint.mapId)
            ConnectionsHandler.getConnection().send(mirmsg)

        elif isinstance(msg, (MapChangeFailedMessage, MapMoveFailed)):
            logger.error(f"Fatal error, restarting bot")
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
                self.doFarm()
            del self._entities[msg.elemId]
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            sleep(0.2)
            logger.debug("-" * 100)
            self._discardedMonstersIds.clear()
            self.reset()
            if self.currMapCoords not in self.parcours.path:
                logger.debug(f"[BotFarmFrame] Map {self.currMapCoords} not in path will switch to autotrip")
                self._inAutoTrip = True
                self._worker.removeFrame(self)
                self._worker.addFrame(BotAutoTripFrame(self.parcours.startMapId))
                return True
            else:
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
            raise Exception(f"No transition found to move to Map {x, y}")

    def doFight(self):
        availableMonsterFights = []
        currPlayerPos = MapPoint.fromCellId(PlayedCharacterManager().currentCellId)
        for entityId in self.entitiesFrame._monstersIds:
            if entityId in self._discardedMonstersIds:
                continue 
            infos: GameRolePlayGroupMonsterInformations = self.entitiesFrame.getEntityInfos(entityId)
            # if infos.staticInfos.mainCreatureLightInfos.level <= int((1 / 2) * PlayedCharacterManager().limitedLevel):
            if len(infos.staticInfos.underlings) <= 3:
                monsterGroupPos = MapPoint.fromCellId(infos.disposition.cellId)
                availableMonsterFights.append(
                    {"info": infos, "distance": currPlayerPos.distanceToCell(monsterGroupPos)}
                )
        if availableMonsterFights:
            availableMonsterFights.sort(key=lambda x: x["distance"])
            entityId = availableMonsterFights[0]["info"].contextualId
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
