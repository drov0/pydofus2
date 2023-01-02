from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.data.AbstractDataManager import AbstractDataManager
from pydofus2.com.ankamagames.jerakine.data.GameDataFileAccessor import GameDataFileAccessor
from pydofus2.com.ankamagames.jerakine.newCache.LruGarbageCollector import LruGarbageCollector
from pydofus2.com.ankamagames.jerakine.newCache.impl.Cache import Cache
from pydofus2.com.ankamagames.jerakine.utils.memory.SoftReference import SoftReference
from pydofus2.com.ankamagames.jerakine.utils.memory.WeakReference import WeakReference

logger = Logger("Dofus2")


class GameData(AbstractDataManager):

    CACHE_SIZE_RATIO: float = 0.1
    _directObjectCaches: dict[str, dict[int, WeakReference]] = dict()
    _objectCaches: dict[str, Cache] = dict()
    _objectsCaches: dict[str, SoftReference] = dict()
    _overrides: dict[str, dict[int, int]] = dict()

    def __init__(self):
        super().__init__()

    @classmethod
    def addOverride(cls, moduleId: str, keyId: int, newKeyId: int) -> None:
        if not cls._overrides.get(moduleId):
            cls._overrides[moduleId] = []
        cls._overrides[moduleId][keyId] = newKeyId

    @classmethod
    def getObject(cls, moduleId: str, keyId: int) -> object:
        if cls._overrides.get(moduleId) and cls._overrides[moduleId].get(keyId):
            keyId = cls._overrides[moduleId][keyId]
        if not cls._directObjectCaches.get(moduleId):
            cls._directObjectCaches[moduleId] = dict()
        else:
            wr = cls._directObjectCaches[moduleId].get(keyId)
            if wr:
                o = wr.object
                if o:
                    return o
        if not cls._objectCaches.get(moduleId):
            cls._objectCaches[moduleId] = Cache(
                GameDataFileAccessor().getCount(moduleId) * cls.CACHE_SIZE_RATIO,
                LruGarbageCollector(),
            )
        else:
            o = cls._objectCaches[moduleId].peek(keyId)
            if o:
                return o
        o = GameDataFileAccessor().getObject(moduleId, keyId)
        cls._directObjectCaches[moduleId][keyId] = WeakReference(o)
        cls._objectCaches[moduleId].store(keyId, o)
        return o

    @classmethod
    def getObjects(cls, moduleId: str) -> list:
        if cls._objectsCaches.get(moduleId):
            objects = cls._objectsCaches[moduleId].object
            if objects:
                return objects
        objects = GameDataFileAccessor().getObjects(moduleId)
        cls._objectsCaches[moduleId] = SoftReference(objects)
        return objects
