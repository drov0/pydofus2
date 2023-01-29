from pydofus2.com.ankamagames.atouin.managers.EntitiesManager import EntitiesManager
from pydofus2.com.ankamagames.dofus.logic.game.misc.IEntityLocalizer import IEntityLocalizer
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import ThreadSharedSingleton
import threading

lock = threading.Lock()


class DofusEntities(metaclass=ThreadSharedSingleton):

    LOCALIZER_DEBUG: bool = True

    def __init__(self) -> None:
        self._localizers = list[IEntityLocalizer]()

    def getEntity(self, entityId: float) -> IEntity:
        for localizer in self._localizers:
            foundEntity = localizer.getEntity(float(entityId))
            if foundEntity:
                return foundEntity
        return EntitiesManager().getEntity(float(entityId))

    def registerLocalizer(self, localizer: IEntityLocalizer) -> None:
        clazz: str = localizer.__class__.__qualname__
        for currentLocalizer in self._localizers:
            currentClazz = currentLocalizer.__class__.__qualname__
            if currentClazz == clazz:
                return
        self._localizers.append(localizer)

    def reset(self) -> None:
        for localizer in self._localizers:
            localizer.unregistered()
        self._localizers.clear()
