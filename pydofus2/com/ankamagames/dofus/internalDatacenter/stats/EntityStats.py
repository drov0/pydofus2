from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.DetailedStats import DetailedStat
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.UsableStat import UsableStat
from pydofus2.damageCalculation.tools.StatIds import StatIds

logger = Logger("Dofus2")


class EntityStats:
    _entityId: float = None
    _stats: dict[str, Stat] = {}

    def __init__(self, entityId: float):
        super().__init__()
        self._entityId = entityId
        self._stats = dict()

    @property
    def entityId(self) -> float:
        return self._entityId

    @property
    def stats(self) -> dict:
        return self._stats

    def getFormattedMessage(self, message: str) -> str:
        return self.__class__.__name__ + " (Entity ID: " + str(self._entityId) + "): " + message

    def setStat(self, stat: Stat, isBulkUpdate: bool = True) -> None:
        # logger.debug(f"Set stat {stat} for entity {self._entityId}")
        stat.entityId = float(self._entityId)
        self._stats[str(stat.id)] = stat

    def getStat(self, statId: float) -> Stat:
        statKey = str(statId)
        if statKey not in self._stats:
            logger.error(self.getFormattedMessage("Stat ID " + statKey + " not found in stats"))
            return None
        return self._stats[statKey]

    def deleteStat(self, statId: float) -> None:
        statKey: str = str(statId)
        if statKey not in self._stats:
            return
        stat: Stat = self._stats[statKey]
        stat.reset()
        del self._stats[statKey]

    def resetStats(self) -> None:
        for stat in self._stats.values():
            stat.reset()
        self._stats = dict()

    def getStatsNumber(self) -> float:
        counter: float = 0
        for _ in self._stats:
            counter += 1
        return counter

    def hasStat(self, statId: float) -> bool:
        return str(statId) in self._stats

    def getStatTotalValue(self, statId: float) -> float:
        key: str = str(statId)
        if key not in self._stats:
            return 0
        stat: Stat = self._stats.get(key)
        return float(stat.totalValue) if stat is not None else float(0)

    def getStatBaseValue(self, statId: float) -> float:
        key: str = str(statId)
        if key not in self._stats:
            return 0
        stat: Stat = self._stats[key]
        if isinstance(stat, DetailedStat):
            return stat.baseValue
        return 0

    def getStatAdditionalValue(self, statId: float) -> float:
        key: str = str(statId)
        if key not in self._stats:
            return 0
        stat: Stat = self._stats[key]
        if isinstance(stat, DetailedStat):
            return stat.additionalValue
        return 0

    def getStatObjectsAndMountBonusValue(self, statId: float) -> float:
        key: str = str(statId)
        if key not in self._stats:
            return 0
        stat: Stat = self._stats[key]
        if isinstance(stat, DetailedStat):
            return stat.objectsAndMountBonusValue
        return 0

    def getStatAlignGiftBonusValue(self, statId: float) -> float:
        key: str = str(statId)
        if key not in self._stats:
            return 0
        stat: Stat = self._stats[key]
        if isinstance(stat, DetailedStat):
            return stat.alignGiftBonusValue
        return 0

    def getStatContextModifValue(self, statId: float) -> float:
        key: str = str(statId)
        if key not in self._stats:
            return 0
        stat: Stat = self._stats[key]
        if isinstance(stat, DetailedStat):
            return stat.contextModifValue
        return 0

    def getStatUsedValue(self, statId: float) -> float:
        key: str = str(statId)
        if key not in self._stats:
            return 0
        stat: Stat = self._stats[key]
        if isinstance(stat, UsableStat):
            return stat.usedValue
        return 0

    def __str__(self) -> str:
        statsDump: str = ""
        for stat in self._stats.values():
            statsDump += "\n\t" + str(stat)
        if not statsDump:
            logger.debug(self._stats)
            statsDump = "\n\tNo stats to display."
        return self.getFormattedMessage(statsDump)

    def getHealthPoints(self) -> float:
        return (
            self.getMaxHealthPoints()
            + self.getStatTotalValue(StatIds.CUR_LIFE)
            + self.getStatTotalValue(StatIds.CUR_PERMANENT_DAMAGE)
        )

    def getMaxHealthPoints(self) -> float:
        vitalityStat: Stat = self.getStat(StatIds.VITALITY)
        effectiveVitality: float = 0
        if isinstance(vitalityStat, DetailedStat):
            detailedVitalityStat = vitalityStat
            effectiveVitality = (
                max(
                    0,
                    detailedVitalityStat.baseValue
                    + detailedVitalityStat.objectsAndMountBonusValue
                    + detailedVitalityStat.additionalValue
                    + detailedVitalityStat.alignGiftBonusValue,
                )
                + detailedVitalityStat.contextModifValue
            )
        elif isinstance(vitalityStat, Stat):
            effectiveVitality = vitalityStat.totalValue
        return (
            self.getStatTotalValue(StatIds.LIFE_POINTS)
            + effectiveVitality
            - self.getStatTotalValue(StatIds.CUR_PERMANENT_DAMAGE)
        )
