from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from pydofus2.com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.abstract.AbstractStatContextualStep import (
    AbstractStatContextualStep,
)
from pydofus2.com.ankamagames.dofus.network.enums.GameContextEnum import GameContextEnum
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.damageCalculation.tools.StatIds import StatIds


class FightLifeVariationStep(AbstractStatContextualStep, IFightStep):

    COLOR: int = 16711680

    BLOCKING: bool = False

    _delta: int

    _permanentDamages: int

    _elementId: int

    _fighterInfo: GameFightFighterInformations = None

    def __init__(self, entityId: float, delta: int, permanentDamages: int, elementId: int):
        super().__init__(self.COLOR, str(delta), entityId, GameContextEnum.FIGHT, self.BLOCKING)
        self._virtual = True
        self._delta = delta
        self._permanentDamages = permanentDamages
        self._elementId = elementId

    @property
    def stepType(self) -> str:
        return "lifeVariation"

    @property
    def value(self) -> int:
        return self._delta

    @property
    def delta(self) -> int:
        return self._delta

    @property
    def permanentDamages(self) -> int:
        return self._permanentDamages

    @property
    def elementId(self) -> int:
        return self._elementId

    def start(self) -> None:
        self._fighterInfo = FightEntitiesFrame.getCurrentInstance().getEntityInfos(self._targetId)
        if not self._fighterInfo:
            Logger().error(f"Can't find fighter info for entity {self._targetId}")
            super().executeCallbacks()
            return
        self.apply()

    def apply(self) -> None:
        stats: EntityStats = StatsManager().getStats(self._targetId)
        res: int = stats.getHealthPoints() + self._delta
        maxLifePoints: float = max(1, stats.getMaxHealthPoints() + self._permanentDamages)
        lifePoints: float = min(max(0, res), maxLifePoints)
        stats.setStat(
            Stat(
                StatIds.CUR_PERMANENT_DAMAGE,
                stats.getStatTotalValue(StatIds.CUR_PERMANENT_DAMAGE) - self._permanentDamages,
            )
        )
        stats.setStat(
            Stat(
                StatIds.CUR_LIFE,
                lifePoints - maxLifePoints - stats.getStatTotalValue(StatIds.CUR_PERMANENT_DAMAGE),
            )
        )

        super().start()
