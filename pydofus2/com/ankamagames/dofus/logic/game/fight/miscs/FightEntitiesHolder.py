from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.common.misc.IEntityLocalizer import (
    IEntityLocalizer,
)
from com.ankamagames.jerakine.entities.interfaces.IDisplayable import IDisplayable
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton

logger = Logger("Dofus2")


class FightEntitiesHolder(IEntityLocalizer, metaclass=Singleton):

    _holdedEntities = dict()

    def __init__(self):
        self._holdedEntities = dict()
        DofusEntities.registerLocalizer(self)
        super().__init__()

    def getEntity(self, entityId: float) -> IEntity:
        return self._holdedEntities.get(entityId)

    def holdEntity(self, entity: IEntity) -> None:
        self._holdedEntities[entity.id] = entity

    def unholdEntity(self, entityId: float) -> None:
        if entityId in self._holdedEntities:
            del self._holdedEntities[entityId]
        # logger.warn("Unholded entity with ID " + str(entityId))

    def reset(self) -> None:
        self._holdedEntities.clear()

    def getEntities(self) -> dict:
        return self._holdedEntities

    def unregistered(self) -> None:
        for entity in self._holdedEntities:
            if isinstance(entity, IDisplayable):
                entity = None
            if isinstance(entity, TiphonSprite):
                entity = None
        self._holdedEntities.clear()
