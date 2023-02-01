from types import FunctionType
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.DetailedStats import DetailedStat
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.UsableStat import UsableStat
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristic import (
    CharacterCharacteristic,
)
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristicDetailed import (
    CharacterCharacteristicDetailed,
)
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristicValue import (
    CharacterCharacteristicValue,
)
from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterUsableCharacteristicDetailed import (
    CharacterUsableCharacteristicDetailed,
)
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton


class StatsManager(metaclass=Singleton):
    DEFAULT_IS_VERBOSE = True
    DATA_STORE_CATEGORY = "ComputerModule_statsManager"
    DATA_STORE_KEY_IS_VERBOSE = "statsManagerIsVerbose"

    def __init__(self):
        self._entityStats = dict()
        self._isVerbose = self.DEFAULT_IS_VERBOSE
        self._statListeners = dict[str, list[FunctionType]]()
        Logger().info("Instantiating stats manager")
        self._isVerbose = self.DEFAULT_IS_VERBOSE

    def setStats(self, stats: EntityStats) -> bool:
        if stats is None:
            Logger().error("Tried to set None stats. Aborting")
            return False
        key = str(float(stats.entityId))
        self._entityStats[key] = stats
        return True

    def getStats(self, entityId: float) -> EntityStats:
        key = str(float(entityId))
        return self._entityStats.get(key)

    def addRawStats(self, entityId: float, rawStats: list[CharacterCharacteristic]) -> None:
        entityKey = str(float(entityId))
        entityStats: EntityStats = self._entityStats.get(entityKey)

        if entityStats is None:
            entityStats = EntityStats(float(entityId))
            self.setStats(entityStats)

        for rawStat in rawStats:
            if isinstance(rawStat, CharacterUsableCharacteristicDetailed):
                rawUsableStat = rawStat
                entityStat = UsableStat(
                    id=rawUsableStat.characteristicId,
                    baseValue=rawUsableStat.base,
                    additionalValue=rawUsableStat.additional,
                    objectsAndMountBonusValue=rawUsableStat.objectsAndMountBonus,
                    alignGiftBonusValue=rawUsableStat.alignGiftBonus,
                    contextModifValue=rawUsableStat.contextModif,
                    usedValue=rawUsableStat.used,
                )
            elif isinstance(rawStat, CharacterCharacteristicDetailed):
                rawDetailedStat: CharacterCharacteristicDetailed = rawStat
                entityStat = DetailedStat(
                    id=rawDetailedStat.characteristicId,
                    baseValue=rawDetailedStat.base,
                    additionalValue=rawDetailedStat.additional,
                    objectsAndMountBonusValue=rawDetailedStat.objectsAndMountBonus,
                    alignGiftBonusValue=rawDetailedStat.alignGiftBonus,
                    contextModifValue=rawDetailedStat.contextModif,
                )
            else:
                if not isinstance(rawStat, CharacterCharacteristicValue):
                    Logger().debug(f"Skipping rawStat {rawStat} of type {type(rawStat)}")
                    continue
                else:
                    entityStat = Stat(rawStat.characteristicId, rawStat.total)
            entityStats.setStat(entityStat, False)

    def deleteStats(self, entityId: float) -> bool:
        entityKey = str(float(entityId))
        if entityKey not in self._entityStats:
            return False
        del self._entityStats[entityKey]
        Logger().info("Stats for entity with ID " + entityKey + " deleted")
        return True
