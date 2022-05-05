from types import FunctionType
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.dofus.internalDatacenter.stats.DetailedStats import DetailedStat
from com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from com.ankamagames.dofus.internalDatacenter.stats.UsableStat import UsableStat
from com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristic import (
    CharacterCharacteristic,
)
from com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristicDetailed import (
    CharacterCharacteristicDetailed,
)
from com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristicValue import (
    CharacterCharacteristicValue,
)
from com.ankamagames.dofus.network.types.game.character.characteristic.CharacterUsableCharacteristicDetailed import (
    CharacterUsableCharacteristicDetailed,
)
from com.ankamagames.jerakine.managers.StoreDataManager import StoreDataManager
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from com.ankamagames.jerakine.types.DataStoreType import DataStoreType
from com.ankamagames.jerakine.types.enums.DataStoreEnum import DataStoreEnum
from damageCalculation.tools.StatIds import StatIds

logger = Logger("pyd2bot")


class StatsManager(metaclass=Singleton):
    DEFAULT_IS_VERBOSE = True
    DATA_STORE_CATEGORY = "ComputerModule_statsManager"
    DATA_STORE_KEY_IS_VERBOSE = "statsManagerIsVerbose"

    def __init__(self):
        self._entityStats = dict()
        self._isVerbose = self.DEFAULT_IS_VERBOSE
        self._statListeners = dict[str, list[FunctionType]]()
        logger.info("Instantiating stats manager")
        self._dataStoreType = DataStoreType(
            self.DATA_STORE_CATEGORY,
            True,
            DataStoreEnum.LOCATION_LOCAL,
            DataStoreEnum.BIND_COMPUTER,
        )
        rawIsVerbose = StoreDataManager().getData(self._dataStoreType, self.DATA_STORE_KEY_IS_VERBOSE)
        self._isVerbose = rawIsVerbose if isinstance(rawIsVerbose, bool) else self.DEFAULT_IS_VERBOSE

    def setStats(self, stats: EntityStats) -> bool:
        # logger.info(
        #     f"Setting stats {stats.__dict__} for entity with ID '{stats.entityId}'"
        # )
        if stats is None:
            logger.error("Tried to set None stats. Aborting")
            return False
        key = str(float(stats.entityId))
        self._entityStats[key] = stats
        return True

    def getStats(self, entityId: float) -> EntityStats:
        key = str(float(entityId))
        # logger.info(f"Getting stats for entity with ID {key}")
        return self._entityStats.get(key)

    def addRawStats(self, entityId: float, rawStats: list[CharacterCharacteristic]) -> None:
        # logger.debug(f"Adding rawStats count {len(rawStats)} for entity with ID {entityId}")
        entityKey = str(float(entityId))
        entityStats: EntityStats = self._entityStats.get(entityKey)
        isCurLifeStatOnly: bool = (
            len(rawStats) == 1 and rawStats[0] is not None and rawStats[0].characteristicId == StatIds.CUR_LIFE
        )
        if entityStats is None:
            entityStats = EntityStats(float(entityId))
            self.setStats(entityStats)

        for rawStat in rawStats:
            # logger.debug(f"update rawStat {rawStat.__dict__}")
            if isinstance(rawStat, CharacterUsableCharacteristicDetailed):

                rawUsableStat = rawStat
                entityStat = UsableStat(
                    id=rawUsableStat.characteristicId,
                    baseValue=rawUsableStat.base,
                    additionalValue=rawUsableStat.additional,
                    objectsAndMountBonusValue=rawUsableStat.objectsAndMountBonus,
                    alignGiftBonusValue=rawUsableStat.alignGiftBonus,
                    contextModifValue=0,
                    usedValue=rawUsableStat.used,
                )
            elif isinstance(rawStat, CharacterCharacteristicDetailed):
                rawDetailedStat: CharacterCharacteristicDetailed = rawStat
                entityStat = DetailedStat(
                    rawDetailedStat.characteristicId,
                    rawDetailedStat.base,
                    rawDetailedStat.additional,
                    rawDetailedStat.objectsAndMountBonus,
                    rawDetailedStat.alignGiftBonus,
                    contextModifValue=0,
                )
            else:
                if not isinstance(rawStat, CharacterCharacteristicValue):
                    logger.debug(f"Skipping rawStat {rawStat} of type {type(rawStat)}")
                    continue
                else:
                    entityStat = Stat(rawStat.characteristicId, rawStat.total)
            entityStats.setStat(entityStat, False)

    def deleteStats(self, entityId: float) -> bool:
        entityKey = str(float(entityId))
        if entityKey not in self._entityStats:
            logger.error("Tried to del stats for entity with ID " + entityKey + ", but none were found. Aborting")
            return False
        del self._entityStats[entityKey]
        logger.info("Stats for entity with ID " + entityKey + " deleted")
        return True

    def isStatHasListener(self, statId: float, listener: FunctionType) -> bool:
        return self.getFeatureListenerIndex(statId, listener) != -1

    def getFeatureListenerIndex(self, statId: float, listener: FunctionType) -> int:
        key: str = str(statId)
        listeners = self._statListeners.get(key)
        if not listeners:
            return -1
        if len(listeners) <= 0:
            del self._statListeners[key]
            return -1
        return self._statListeners[key].index(listener)

    def addListenerToStat(self, statId: float, listener: FunctionType) -> bool:
        if listener is None:
            logger.error("Listener provided is None")
            return False
        isListenerAdded: bool = False
        key: str = str(float(statId))
        if not self.isStatHasListener(statId, listener):
            if not self._statListeners.get(key):
                self._statListeners[key] = list[FunctionType]()
            self._statListeners[key].append(listener)
            isListenerAdded = True
        if isListenerAdded:
            logger.info(f"Listener {listener.__name__}{listener.__annotations__} added to stat with ID " + key)
        else:
            logger.error(
                f"Listener {listener.__name__}{listener.__annotations__} could NOT be added to stat with ID " + key
            )
        return isListenerAdded

    def removeListenerFromStat(self, statId: float, listener: FunctionType) -> bool:
        if listener is None:
            logger.error("Listener provided is None")
            return False
        isListenerRemoved: bool = False
        key: str = str(float(statId))
        if self.isStatHasListener(statId, listener):
            self._statListeners[key].remove(listener)
            isListenerRemoved = True
        if isListenerRemoved:
            logger.info(f"Listener {listener.__name__}{listener.__annotations__} removed from stat with ID " + key)
        else:
            logger.error(
                f"Listener {listener.__name__}{listener.__annotations__} could NOT be removed from stat with ID " + key
            )
        return isListenerRemoved
