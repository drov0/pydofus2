import threading
from types import FunctionType

from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.DetailedStats import \
    DetailedStat
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.EntityStats import \
    EntityStats
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.UsableStat import \
    UsableStat
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristic import \
    CharacterCharacteristic
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristicDetailed import \
    CharacterCharacteristicDetailed
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristicValue import \
    CharacterCharacteristicValue
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterUsableCharacteristicDetailed import \
    CharacterUsableCharacteristicDetailed
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.logger.MemoryProfiler import \
    MemoryProfiler
from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import \
    ThreadSharedSingleton


class StatsManager(metaclass=ThreadSharedSingleton):
    DEFAULT_IS_VERBOSE = True
    DATA_STORE_CATEGORY = "ComputerModule_statsManager"
    DATA_STORE_KEY_IS_VERBOSE = "statsManagerIsVerbose"

    def __init__(self):
        self._entityStats = dict()
        self._isVerbose = self.DEFAULT_IS_VERBOSE
        self._lock = threading.RLock()

    def setStats(self, stats: EntityStats) -> bool:
        key = float(stats.entityId)
        with self._lock:
            self._entityStats[key] = stats
        return True

    def getStats(self, entityId: float) -> EntityStats:
        stats = self._entityStats.get(float(entityId))
        return stats
    
    def addRawStats(self, entityId: float, rawStats: list[CharacterCharacteristic]) -> None:
        entityId = float(entityId)
        with self._lock:
            entityStats = self.getStats(entityId)
            if not entityStats:
                entityStats = EntityStats(entityId)
                self.setStats(entityStats)
            for rawStat in rawStats:
                if isinstance(rawStat, CharacterUsableCharacteristicDetailed):
                    entityStat = UsableStat(
                        id=rawStat.characteristicId,
                        baseValue=rawStat.base,
                        additionalValue=rawStat.additional,
                        objectsAndMountBonusValue=rawStat.objectsAndMountBonus,
                        alignGiftBonusValue=rawStat.alignGiftBonus,
                        contextModifValue=rawStat.contextModif,
                        usedValue=rawStat.used,
                    )
                elif isinstance(rawStat, CharacterCharacteristicDetailed):
                    entityStat = DetailedStat(
                        id=rawStat.characteristicId,
                        baseValue=rawStat.base,
                        additionalValue=rawStat.additional,
                        objectsAndMountBonusValue=rawStat.objectsAndMountBonus,
                        alignGiftBonusValue=rawStat.alignGiftBonus,
                        contextModifValue=rawStat.contextModif,
                    )
                elif isinstance(rawStat, CharacterCharacteristicValue):
                    entityStat = Stat(rawStat.characteristicId, rawStat.total)
                else:
                    Logger().error(f"[StatsManager] Unknown raw stat type: {type(rawStat).__name__}")
                    continue
                entityStats.setStat(entityStat, False)

    def purgeNonPlayersStats(self) -> None:
        with self._lock:
            from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
                PlayedCharacterManager
            keys = list(self._entityStats.keys())
            players: list[PlayedCharacterManager] = PlayedCharacterManager.getInstances()
            playersIDs = [float(player.id) for player in players]
            for ctxid in keys:
                if ctxid not in playersIDs:
                    Logger().debug(f"[StatsManager] Purge stats of non player {ctxid}")
                    del self._entityStats[ctxid]

    def deleteStats(self, entityId: float) -> bool:
        from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
                PlayedCharacterManager
        with self._lock:
            playersIDs = [float(player.id) for player in PlayedCharacterManager.getInstances()]
            entityId = float(entityId)
            if entityId in playersIDs:
                return
            if entityId not in self._entityStats:
                return False
            del self._entityStats[entityId]
            return True
