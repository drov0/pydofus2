from pydofus2.com.ankamagames.berilia.types.LocationEnum import LocationEnum
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from pydofus2.com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from pydofus2.com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from pydofus2.com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.abstract.AbstractStatContextualStep import (
    AbstractStatContextualStep,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from pydofus2.com.ankamagames.dofus.network.enums.GameContextEnum import GameContextEnum
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightCharacterInformations import (
    GameFightCharacterInformations,
)
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from pydofus2.com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from pydofus2.com.ankamagames.jerakine.utils.display.EnterFrameDispatcher import (
    EnterFrameDispatcher,
)
from pydofus2.damageCalculation.tools.StatIds import StatIds


class FightShieldPointsVariationStep(AbstractStatContextualStep, IFightStep):

    COLOR: int = 10053324

    BLOCKING: bool = False

    _intValue: int

    _elementId: int

    _entityStats: EntityStats = None

    _newShieldStat: Stat = None

    _fighterInfo: GameFightFighterInformations = None

    _target: AnimatedCharacter = None

    def __init__(self, entityId: float, value: int, elementId: int):
        super().__init__(
            self.COLOR, str(value), entityId, GameContextEnum.FIGHT, self.BLOCKING
        )
        self._intValue = value
        self._elementId = elementId
        self._virtual = False
        self._entityStats = StatsManager().getStats(self._targetId)
        if self._entityStats is not None:
            self._newShieldStat = self._entityStats.getStat(StatIds.SHIELD)

    @property
    def stepType(self) -> str:
        return "shieldPointsVariation"

    @property
    def value(self) -> int:
        return self._intValue

    @property
    def virtual(self) -> bool:
        return self._virtual

    @virtual.setter
    def virtual(self, pValue: bool) -> None:
        self._virtual = pValue

    def start(self) -> None:
        self._target = DofusEntities.getEntity(self._targetId)
        self._fighterInfo = FightEntitiesFrame.getCurrentInstance().getEntityInfos(
            self._targetId
        )
        if not self._fighterInfo:
            super().executeCallbacks()
            return
        EnterFrameDispatcher().worker.addSingleTreatment(self, self.apply, [])

    def apply(self) -> None:
        if self._intValue < 0:
            FightEventsHelper().sendFightEvent(
                FightEventEnum.FIGHTER_SHIELD_LOSS,
                [self._targetId, abs(self._intValue), self._elementId],
                self._targetId,
                self.castingSpellId,
            )
        elif self._intValue == 0:
            FightEventsHelper().sendFightEvent(
                FightEventEnum.FIGHTER_NO_CHANGE,
                [self._targetId],
                self._targetId,
                self.castingSpellId,
            )
        super().start()

    def onAnimationEnd(self, pEvent) -> None:
        self.start()
