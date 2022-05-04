from com.ankamagames.dofus.internalDatacenter.spells.SpellWrapper import SpellWrapper
from com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.steps.abstract.AbstractStatContextualStep import (
    AbstractStatContextualStep,
)
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.dofus.network.enums.GameContextEnum import GameContextEnum
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.utils.display.EnterFrameDispatcher import (
    EnterFrameDispatcher,
)
from damageCalculation.tools.StatIds import StatIds

logger = Logger(__name__)


class FightActionPointsVariationStep(AbstractStatContextualStep, IFightStep):

    COLOR: int = 255

    BLOCKING: bool = False

    _intValue: int

    _voluntarlyUsed: bool

    _updateFighterInfos: bool

    _showChatmessage: bool

    def __init__(
        self,
        entityId: float,
        value: int,
        voluntarlyUsed: bool,
        updateFighterInfos: bool = True,
        showChatmessage: bool = True,
    ):
        updateFighterInfos = False
        super().__init__(
            self.COLOR,
            "+" + value if value > 0 else str(value),
            entityId,
            GameContextEnum.FIGHT,
            self.BLOCKING,
        )
        self._showChatmessage = showChatmessage
        self._intValue = value
        self._voluntarlyUsed = voluntarlyUsed
        self._virtual = True
        self._updateFighterInfos = updateFighterInfos

    @property
    def stepType(self) -> str:
        return "actionPointsVariation"

    @property
    def value(self) -> int:
        return self._intValue

    @property
    def voluntarlyUsed(self) -> bool:
        return self._voluntarlyUsed

    def start(self) -> None:
        stats: EntityStats = StatsManager().getStats(self._targetId)
        ap: Stat = stats.getStat(StatIds.ACTION_POINTS)
        newValue = ap.totalValue + self._intValue
        stats.setStat(Stat(StatIds.ACTION_POINTS, newValue))
        logger.debug(f"new ap value : {newValue}")
        SpellWrapper.refreshAllPlayerSpellHolder(self._targetId)
        super().start()
