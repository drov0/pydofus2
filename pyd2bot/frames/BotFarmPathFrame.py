from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapInformationsRequestMessage import (
    MapInformationsRequestMessage,
)
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition
from com.ankamagames.dofus.logic.game.fight.messages.FightRequestFailed import FightRequestFailed
from com.ankamagames.dofus.logic.game.fight.messages.MapMoveFailed import MapMoveFailed
from com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayGroupMonsterInformations import (
    GameRolePlayGroupMonsterInformations,
)
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
from pyd2bot.enums.ServerNotificationTitlesEnum import ServerNotificationTitlesEnum
from pyd2bot.frames.BotAutoTripFrame import BotAutoTripFrame
from pyd2bot.messages.AutoTripEndedMessage import AutoTripEndedMessage
from pyd2bot.models.farmPaths.AbstractFarmPath import AbstractFarmPath

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import (
        RoleplayInteractivesFrame,
    )
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import (
        RoleplayEntitiesFrame,
    )
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame

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
        self._followingIe = -1
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

    def pushed(self) -> bool:
        if self._autoStart:
            self.doFarm()
        return True

    def pulled(self) -> bool:
        self.reset()
        return True

    def reset(self):
        self._followingMapchange = -1
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

        if isinstance(msg, AutoTripEndedMessage):
            self._inAutoTrip = False
            if msg.mapId is None:
                raise Exception("Auto trip was Unable to reach destination")
            self.doFarm()

        elif isinstance(msg, InteractiveUseErrorMessage):
            logger.error(
                f"[BotFarmFrame] Error unable to use interactive element {msg.elemId} with the skill {msg.skillInstanceUid}"
            )
            logger.debug("*" * 80)
            if msg.elemId == self._followingIe:
                self.reset()
                logger.debug("Will move on")
                del self.interactivesFrame._ie[msg.elemId]
                del self.interactivesFrame._collectableIe[msg.elemId]
                self.doFarm()
            return True

        elif isinstance(msg, (FightRequestFailed, MapMoveFailed, MapChangeFailedMessage)):
            self.requestMapData()

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
            logger.debug("-" * 100)
            if not self._inAutoTrip:
                self.reset()
                self.doFarm()
                return True
            return False

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
        currPlayerPos = MapPoint.fromCellId(PlayedCharacterManager().currentCellId)
        for entityId in self.entitiesFrame._monstersIds:
            if entityId in self._discardedMonstersIds:
                continue
            infos: GameRolePlayGroupMonsterInformations = self.entitiesFrame.getEntityInfos(entityId)
            totalGrpLvl = infos.staticInfos.mainCreatureLightInfos.level + sum([ul.level for ul in infos.staticInfos.underlings])
            if totalGrpLvl < 1.5 * PlayedCharacterManager().limitedLevel:
                monsterGroupPos = MapPoint.fromCellId(infos.disposition.cellId)
                availableMonsterFights.append({"info": infos, "distance": currPlayerPos.distanceToCell(monsterGroupPos)})
        if availableMonsterFights:
            availableMonsterFights.sort(key=lambda x: x["distance"])
            entityId = availableMonsterFights[0]["info"].contextualId
            self._followinMonsterGroup = entityId
            self.movementFrame.attackMonsters(entityId)

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
            self.collectResource(skills=self.farmPath.skills)
        if self._followingIe is None and self._followinMonsterGroup is None:
            self.moveToNextStep()

    def requestMapData(self):
        mirmsg = MapInformationsRequestMessage()
        mirmsg.init(mapId_=MapDisplayManager().currentMapPoint.mapId)
        ConnectionsHandler.getConnection().send(mirmsg)

    def collectResource(self, skills=[]) -> None:
        ce = None
        for it in self.interactivesFrame.collectables.values():
            if it.enabled:
                if skills and it.skill.id not in skills:
                    continue
                ce = it
                elementId = it.id
                break
        if ce is not None and ce.enabled:
            logger.info(f"[BotFarmFrame] Collecting {ce} ... skillId : {ce.skill.id}")
            ie = self.interactivesFrame.interactives.get(elementId)
            if ie is None:
                raise Exception(f"[BotFarmFrame] InteractiveElement {elementId} not found!!!")
            self._followingIe = ie
            self.interactivesFrame.skillClicked(ie)
