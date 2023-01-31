from pydofus2.com.ankamagames.jerakine.data.AbstractDataManager import AbstractDataManager
from pydofus2.com.ankamagames.jerakine.data.GameDataFileAccessor import GameDataFileAccessor
from pydofus2.com.ankamagames.jerakine.newCache.impl.Cache import Cache
from pydofus2.com.ankamagames.jerakine.utils.memory.WeakReference import WeakReference


class GameData(AbstractDataManager):

    def __init__(self):
        super().__init__()

    @classmethod
    def getObject(cls, moduleId: str, keyId: int) -> object:
        return GameDataFileAccessor().getObject(moduleId, keyId)

    @classmethod
    def getObjects(cls, moduleId: str) -> list:
        return GameDataFileAccessor().getObjects(moduleId)
