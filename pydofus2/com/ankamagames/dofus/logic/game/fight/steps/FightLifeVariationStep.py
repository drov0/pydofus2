from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from com.ankamagames.dofus.logic.game.fight.steps.abstract.AbstractStatContextualStep import (
    AbstractStatContextualStep,
)
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.dofus.network.enums.GameContextEnum import GameContextEnum
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from com.ankamagames.jerakine.utils.display.EnterFrameDispatcher import (
    EnterFrameDispatcher,
)
from damageCalculation.tools.StatIds import StatIds


class FightLifeVariationStep(AbstractStatContextualStep, IFightStep):

    COLOR: int = 16711680

    BLOCKING: bool = False

    _delta: int

    _permanentDamages: int

    _elementId: int

    skipTextEvent: bool = False

    _fighterInfo: GameFightFighterInformations = None

    def __init__(
        self, entityId: float, delta: int, permanentDamages: int, elementId: int
    ):
        super().__init__(
            self.COLOR, str(delta), entityId, GameContextEnum.FIGHT, self.BLOCKING
        )
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
        self._fighterInfo = FightEntitiesFrame.getCurrentInstance().getEntityInfos(
            self._targetId
        )
        if not self._fighterInfo:
            super().executeCallbacks()
            return
        EnterFrameDispatcher().worker.addSingleTreatment(self, self.apply, [])

    def apply(self) -> None:
        stats: EntityStats = StatsManager().getStats(self._targetId)
        res: int = stats.getHealthPoints() + self._delta
        maxLifePoints: float = max(
            1, stats.getMaxHealthPoints() + self._permanentDamages
        )
        lifePoints: float = min(max(0, res), maxLifePoints)
        stats.setStat(
            Stat(
                StatIds.CUR_PERMANENT_DAMAGE,
                stats.getStatTotalValue(StatIds.CUR_PERMANENT_DAMAGE)
                - self._permanentDamages,
            )
        )
        stats.setStat(
            Stat(
                StatIds.CUR_LIFE,
                lifePoints
                - maxLifePoints
                - stats.getStatTotalValue(StatIds.CUR_PERMANENT_DAMAGE),
            )
        )
        if self._delta < 0 or self._delta == 0 and not self.skipTextEvent:
            FightEventsHelper().sendFightEvent(
                FightEventEnum.FIGHTER_LIFE_LOSS,
                [self._targetId, abs(self._delta), self._elementId],
                self._targetId,
                self.castingSpellId,
                False,
                2,
            )
        elif self._delta > 0:
            FightEventsHelper().sendFightEvent(
                FightEventEnum.FIGHTER_LIFE_GAIN,
                [self._targetId, abs(self._delta), self._elementId],
                self._targetId,
                self.castingSpellId,
                False,
                2,
            )
        if self._permanentDamages < 0:
            FightEventsHelper().sendFightEvent(
                FightEventEnum.FIGHTER_PERMANENT_DAMAGE,
                [self._targetId, abs(self._permanentDamages), self._elementId],
                self._targetId,
                self.castingSpellId,
                False,
                2,
            )
