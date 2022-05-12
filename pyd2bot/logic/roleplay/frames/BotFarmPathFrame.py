from typing import TYPE_CHECKING
from com.DofusClient import DofusClient

from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.datacenter.notifications.Notification import Notification
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.logic.game.fight.messages.FightRequestFailed import FightRequestFailed
from com.ankamagames.dofus.logic.game.fight.messages.MapMoveFailed import MapMoveFailed
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder
from com.ankamagames.dofus.network.messages.game.context.GameMapMovementCancelMessage import (
    GameMapMovementCancelMessage,
)
from com.ankamagames.dofus.network.messages.game.context.notification.NotificationByServerMessage import (
    NotificationByServerMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapChangeFailedMessage import MapChangeFailedMessage
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapInformationsRequestMessage import (
    MapInformationsRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUsedMessage import InteractiveUsedMessage
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseEndedMessage import (
    InteractiveUseEndedMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseErrorMessage import (
    InteractiveUseErrorMessage,
)
from com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayGroupMonsterInformations import (
    GameRolePlayGroupMonsterInformations,
)
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from pyd2bot.apis.InventoryAPI import InventoryAPI
from pyd2bot.apis.MoveAPI import MoveAPI
from pyd2bot.logic.roleplay.frames.BotAutoTripFrame import BotAutoTripFrame
from pyd2bot.logic.roleplay.messages.AutoTripEndedMessage import AutoTripEndedMessage
from pyd2bot.models.enums.ServerNotificationTitlesEnum import ServerNotificationTitlesEnum
from pyd2bot.models.farmPaths.AbstractFarmPath import AbstractFarmPath

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import RoleplayEntitiesFrame
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import RoleplayInteractivesFrame
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayWorldFrame import RoleplayWorldFrame

logger = Logger("Dofus2")


def GetNextMap(path, index):
    return path[index]


class BotFarmPathFrame(Frame):
    farmPath: AbstractFarmPath = None

    def __init__(self, autoStart: bool = False):
        if not BotFarmPathFrame.farmPath:
            raise Exception("No parcours loaded")
        super().__init__()
        self._autoStart = autoStart
        self._followingIe = None
        self._usingInteractive = False
        self._followingMapchange = -1
        self._entities = dict()
        self._inAutoTrip = False
        self._discardedMonstersIds = []
        self._worker = Kernel().getWorker()

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    @property
    def entitiesFrame(self) -> "RoleplayEntitiesFrame":
        return self._worker.getFrame("RoleplayEntitiesFrame")

    @property
    def interactivesFrame(self) -> "RoleplayInteractivesFrame":
        return self._worker.getFrame("RoleplayInteractivesFrame")

    @property
    def movementFrame(self) -> "RoleplayMovementFrame":
        return self._worker.getFrame("RoleplayMovementFrame")

    @property
    def worldFrame(self) -> "RoleplayWorldFrame":
        return self._worker.getFrame("RoleplayWorldFrame")

    def pushed(self) -> bool:
        if self._autoStart:
            self.doFarm()
        return True

    def pulled(self) -> bool:
        self.reset()
        return True

    def reset(self):
        self._followingMapchange = None
        self._followingIe = None
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

        if isinstance(msg, AutoTripEndedMessage):
            self._inAutoTrip = False
            if msg.mapId is None:
                raise Exception("Auto trip was Unable to reach destination")
            self.doFarm()

        elif isinstance(msg, InteractiveUseErrorMessage):
            if self._inAutoTrip:
                return False
            logger.error(
                f"[BotFarmFrame] Error unable to use interactive element {msg.elemId} with the skill {msg.skillInstanceUid}"
            )
            logger.debug("*" * 80)
            if msg.elemId == self._followingIe.element.elementId:
                if self._entities.get(msg.elemId):
                    del self.interactivesFrame._ie[msg.elemId]
                    del self.interactivesFrame._collectableIe[msg.elemId]
                    self.doFarm()
                else:
                    self.reset()
                    self.requestMapData()
            return True

        elif isinstance(msg, GameMapMovementCancelMessage):
            if self._followingIe:
                del self.interactivesFrame._ie[self._followingIe.element.elementId]
                del self.interactivesFrame._collectableIe[self._followingIe.element.elementId]
                self.reset()
                self.doFarm()
            return True

        elif isinstance(msg, (FightRequestFailed, MapMoveFailed, MapChangeFailedMessage)):
            if self._inAutoTrip:
                return False
            self.requestMapData()

        elif isinstance(msg, InteractiveUsedMessage):
            if self._inAutoTrip:
                return False
            if PlayedCharacterManager().id == msg.entityId and msg.duration > 0:
                logger.debug(f"[BotFarmFrame] Inventory weight {InventoryAPI.getWeightPercent():.2f}%")
                logger.debug(f"[BotFarmFrame] Started using interactive element {msg.elemId} ....")
                if msg.duration > 0:
                    self._usingInteractive = True
            self._entities[msg.elemId] = msg.entityId
            return True

        elif isinstance(msg, InteractiveUseEndedMessage):
            if self._inAutoTrip:
                return False
            if self._entities[msg.elemId] == PlayedCharacterManager().id:
                self._followingIe = None
                self._usingInteractive = False
                logger.debug(f"[BotFarmFrame] Interactive element {msg.elemId} use ended")
                logger.debug("*" * 100)
                self.doFarm()
            del self._entities[msg.elemId]
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            if self._inAutoTrip:
                return False
            logger.debug("-" * 100)
            self.reset()
            self.doFarm()
            return True

        elif isinstance(msg, NotificationByServerMessage):
            notification = Notification.getNotificationById(msg.id)
            if notification.titleId == ServerNotificationTitlesEnum.FULL_PODS:
                logger.debug("[BotFarmFrame] Full pod reached will unload in bank")
                if not self._worker.contains("UnloadInBankFrame"):
                    raise Exception("Full pods but UnloadInBankFrame not found")
            return True

    def moveToNextStep(self):
        self._currTransition = next(self.farmPath)
        logger.debug(
            f"[BotFarmFrame] Current Map {PlayedCharacterManager().currentMap.mapId} Moving to {self._currTransition.transitionMapId}"
        )
        MoveAPI.followTransition(self._currTransition)

    def attackMonsterGroup(self):
        availableMonsterFights = []
        currPlayerPos = PlayedCharacterManager().entity.position
        for entityId in self.entitiesFrame._monstersIds:
            if entityId in self._discardedMonstersIds:
                continue
            infos: GameRolePlayGroupMonsterInformations = self.entitiesFrame.getEntityInfos(entityId)
            if self.insideCurrentPlayerZoneRp(infos.disposition.cellId):
                totalGrpLvl = infos.staticInfos.mainCreatureLightInfos.level + sum(
                    [ul.level for ul in infos.staticInfos.underlings]
                )
                if totalGrpLvl < self.farmPath.monsterLvlCoefDiff * PlayedCharacterManager().limitedLevel:
                    monsterGroupPos = MapPoint.fromCellId(infos.disposition.cellId)
                    availableMonsterFights.append(
                        {"info": infos, "distance": currPlayerPos.distanceToCell(monsterGroupPos)}
                    )
        if availableMonsterFights:
            availableMonsterFights.sort(key=lambda x: x["distance"])
            entityId = availableMonsterFights[0]["info"].contextualId
            self._followinMonsterGroup = entityId
            self.movementFrame.attackMonsters(entityId)

    def insideCurrentPlayerZoneRp(self, cellId):
        tgtRpZone = MapDisplayManager().dataMap.cells[cellId].linkedZoneRP
        return tgtRpZone == PlayedCharacterManager().currentZoneRp

    def doFarm(self):
        if WorldPathFinder().currPlayerVertex not in self.farmPath:
            logger.debug(
                f"[BotFarmFrame] Map {WorldPathFinder().currPlayerVertex.mapId} not in farm path will switch to autotrip"
            )
            self._inAutoTrip = True
            self._worker.addFrame(BotAutoTripFrame(self.farmPath.startVertex.mapId))
            return
        self._followinMonsterGroup = None
        self._followingIe = None
        self._lastCellId = PlayedCharacterManager().currentCellId
        if self.farmPath.fightOnly:
            self.attackMonsterGroup()
        else:
            self.collectResource()
        if self._followingIe is None and self._followinMonsterGroup is None:
            self.moveToNextStep()

    def requestMapData(self):
        mirmsg = MapInformationsRequestMessage()
        mirmsg.init(mapId_=MapDisplayManager().currentMapPoint.mapId)
        ConnectionsHandler.getConnection().send(mirmsg)

    def collectResource(self) -> None:
        target = None
        minDist = float("inf")
        for it in self.interactivesFrame.collectables.values():
            if it.enabled:
                if self.farmPath.jobIds:
                    if it.skill.parentJobId not in self.farmPath.jobIds:
                        continue
                    if PlayedCharacterManager().jobs[it.skill.parentJobId].jobLevel < it.skill.levelMin:
                        continue
                ie = self.interactivesFrame.interactives.get(it.id)
                if not (self.interactivesFrame and self.interactivesFrame.usingInteractive):
                    playerEntity = PlayedCharacterManager().entity
                    if not playerEntity:
                        return
                    nearestCell, _ = self.worldFrame.getNearestCellToIe(ie.element, ie.position)
                    if self.insideCurrentPlayerZoneRp(nearestCell.cellId):
                        dist = PlayedCharacterManager().entity.position.distanceToCell(ie.position)
                        if dist < minDist:
                            target = ie
                            minDist = dist

        if target:
            self._followingIe = ie
            if minDist != 0:
                self.movementFrame.setFollowingInteraction(
                    {
                        "ie": ie.element,
                        "skillInstanceId": ie.skillUID,
                        "additionalParam": 0,
                    }
                )
                self.movementFrame.resetNextMoveMapChange()
                self.movementFrame.askMoveTo(nearestCell)
            else:
                self.movementFrame.activateSkill(ie.skillUID, ie.element.elementId, 0)
            logger.info(f"[BotFarmFrame] Collecting {ie.element.elementId} ... skillId : {ie.skillUID}")