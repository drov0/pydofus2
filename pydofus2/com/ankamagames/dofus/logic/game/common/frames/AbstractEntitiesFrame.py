import com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager as pcm
from com.ankamagames.atouin.managers.EntitiesManager import EntitiesManager
from com.ankamagames.dofus.datacenter.monsters.Monster import Monster
from com.ankamagames.dofus.internalDatacenter.world.WorldPointWrapper import WorldPointWrapper
from com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.network.messages.game.context.EntityDispositionInformations import (
    EntityDispositionInformations,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightMonsterInformations import (
    GameFightMonsterInformations,
)
from com.ankamagames.dofus.network.types.game.context.GameContextActorInformations import GameContextActorInformations
from com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayHumanoidInformations import (
    GameRolePlayHumanoidInformations,
)
from com.ankamagames.dofus.network.types.game.interactive.InteractiveElement import InteractiveElement
from com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint

logger = Logger("Dofus2")


class AbstractEntitiesFrame(Frame):
    def __init__(self):
        self._entities = dict()

        self._entitiesTotal: int = 0

        self._creaturesMode: bool = False

        self._creaturesLimit: int = -1

        self._entitiesVisibleNumber: int = 0

        self._untargetableEntities: bool = False

        self._interactiveElements = list[InteractiveElement]()

        self._currentSubAreaId: int = None

        self._worldPoint: WorldPointWrapper = None

        self._creaturesFightMode: bool = False

        self._justSwitchingCreaturesFightMode: bool = False

        self._entitiesIconsCounts = dict()

        self._entitiesIconsNames = dict()

        self._entitiesIcons = dict()

        self._entitiesIconsOffsets = dict()

        self._carriedEntities = dict()

        self._pendingCarriedEntities = dict()

        self._updateAllIcons: bool = None

        self._showIcons: bool = True

        self._isShowIconsChanged: bool = False

        super().__init__()

    def pulled(self) -> bool:
        self._entities = None
        self._entitiesTotal = 0
        return True

    @property
    def entities(self):
        return self._entities

    @property
    def priority(self) -> int:
        return Priority.NORMAL

    def pushed(self) -> bool:
        self._entities = dict()
        self._entitiesTotal = 0
        return True

    @property
    def interactiveElements(self) -> list[InteractiveElement]:
        return self._interactiveElements

    def process(msg: Message) -> bool:
        raise NotImplementedError()

    def getEntityInfos(self, entityId: float) -> GameContextActorInformations:
        if entityId == 0 or entityId is None:
            return None
        entityId = float(entityId)
        if not self._entities or not self._entitiesTotal:
            return None
        if not self._entities.get(entityId):
            # logger.error(f"Entity {entityId} is unknown. Available actor Ids are {list(self._entities.keys())}")
            if entityId <= EntitiesManager.RANDOM_ENTITIES_ID_START:
                return None
            return None
        return self._entities.get(entityId)

    def updateEntityCellId(self, entityId, cellId) -> None:
        entityId = float(entityId)
        info = self.getEntityInfos(entityId)
        if info:
            info.disposition.cellId = cellId
            self._entities[entityId] = info

    def getEntitiesIdsList(self) -> list[float]:
        entitiesList = [gcai.contextualId for gcai in self._entities.values()]
        return entitiesList

    def hasEntity(self, entityId: float) -> bool:
        return self._entities is not None and self._entitiesTotal > 0 and entityId in self._entities

    def registerActor(self, infos: GameContextActorInformations) -> None:
        self.registerActorWithId(infos, infos.contextualId)

    def registerActorWithId(self, infos: GameContextActorInformations, actorId: float) -> None:
        actorId = float(actorId)
        if self._entities is None:
            self._entities = dict[int, GameContextActorInformations]()
        if not self._entities.get(actorId):
            self._entitiesTotal += 1
        self._entities[actorId] = infos
        if isinstance(infos, GameFightFighterInformations):
            StatsManager().addRawStats(actorId, infos.stats.characteristics.characteristics)

    def unregisterActor(self, actorId: float) -> None:
        actorId = float(actorId)
        if self._entities.get(actorId):
            self._entitiesTotal -= 1
            del self._entities[actorId]
        StatsManager().deleteStats(actorId)

    def addOrUpdateActor(self, infos: GameContextActorInformations) -> AnimatedCharacter:
        characterEntity: AnimatedCharacter = DofusEntities.getEntity(infos.contextualId)
        self.registerActor(infos)
        if isinstance(infos, GameFightFighterInformations):
            StatsManager().addRawStats(infos.contextualId, infos.stats.characteristics.characteristics)
        if characterEntity is None:
            characterEntity = AnimatedCharacter(infos.contextualId)
            if isinstance(infos, GameFightMonsterInformations):
                characterEntity.speedAdjust = Monster.getMonsterById(infos.creatureGenericId).speedAdjust
            EntitiesManager().addAnimatedEntity(float(infos.contextualId), characterEntity)
        if isinstance(infos, GameRolePlayHumanoidInformations):
            humanoid = infos
            if int(infos.contextualId) == int(pcm.PlayedCharacterManager().id):
                pcm.PlayedCharacterManager().restrictions = humanoid.humanoidInfo.restrictions
        if infos.disposition.cellId != -1:
            characterEntity.position = MapPoint.fromCellId(infos.disposition.cellId)
        # logger.debug(f"addOrUpdateActor new actor added {infos.contextualId} position is {characterEntity.position}")

        return characterEntity

    def updateActorDisposition(self, actorId: float, newDisposition: EntityDispositionInformations) -> None:
        actorId = float(actorId)
        if self._entities.get(actorId):
            self._entities[actorId].disposition = newDisposition
        else:
            logger.error(f"Cannot update unknown actor disposition ({actorId}) in informations.")

    def removeActor(self, actorId: float) -> None:
        self.unregisterActor(actorId)

    def addCarrier(
        self,
        carrierEntity: AnimatedCharacter,
        carriedEntity: AnimatedCharacter,
        isPending: bool = False,
    ) -> None:
        if carrierEntity is None or carriedEntity is None:
            return

        if carriedEntity.id in self._pendingCarriedEntities:
            del self._pendingCarriedEntities[carriedEntity.id]

        if carriedEntity.id in self._entitiesIcons:
            self._carriedEntities[carriedEntity.id] = carrierEntity

        elif isPending:
            self._pendingCarriedEntities[carriedEntity.id] = {
                "carrierEntity": carrierEntity,
                "carriedEntity": carriedEntity,
            }
