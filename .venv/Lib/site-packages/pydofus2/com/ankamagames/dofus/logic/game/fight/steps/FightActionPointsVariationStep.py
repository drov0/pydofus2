from pydofus2.com.ankamagames.dofus.internalDatacenter.spells.SpellWrapper import SpellWrapper
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from pydofus2.com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from pydofus2.com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.abstract.AbstractStatContextualStep import (
    AbstractStatContextualStep,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from pydofus2.com.ankamagames.dofus.network.enums.GameContextEnum import GameContextEnum
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.utils.display.EnterFrameDispatcher import (
    EnterFrameDispatcher,
)
from pydofus2.damageCalculation.tools.StatIds import StatIds

logger = Logger("Dofus2")


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
        SpellWrapper.refreshAllPlayerSpellHolder(self._targetId)
        super().start()
