from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.data.AbstractDataManager import AbstractDataManager
from pydofus2.com.ankamagames.jerakine.data.GameDataFileAccessor import GameDataFileAccessor
from pydofus2.com.ankamagames.jerakine.newCache.LruGarbageCollector import LruGarbageCollector
from pydofus2.com.ankamagames.jerakine.newCache.impl.Cache import Cache
from pydofus2.com.ankamagames.jerakine.utils.memory.SoftReference import SoftReference
from pydofus2.com.ankamagames.jerakine.utils.memory.WeakReference import WeakReference


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
        return GameDataFileAccessor().getObject(moduleId, keyId)

    @classmethod
    def getObjects(cls, moduleId: str) -> list:
        return GameDataFileAccessor().getObjects(moduleId)
