from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from pydofus2.com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
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
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.utils.display.EnterFrameDispatcher import (
    EnterFrameDispatcher,
)
from pydofus2.damageCalculation.tools.StatIds import StatIds

logger = Logger("Dofus2")


class FightMovementPointsVariationStep(AbstractStatContextualStep, IFightStep):

    COLOR: int = 26112

    BLOCKING: bool = False

    _intValue: int

    _voluntarlyUsed: bool

    _updateCharacteristicManager: bool

    _showChatmessage: bool

    def __init__(
        self,
        entityId: float,
        value: int,
        voluntarlyUsed: bool,
        updateCharacteristicManager: bool = True,
        showChatMessage: bool = True,
    ):
        super().__init__(
            self.COLOR,
            "+" + str(value) if value > 0 else str(value),
            entityId,
            GameContextEnum.FIGHT,
            self.BLOCKING,
        )
        self._showChatmessage = showChatMessage
        self._intValue = value
        self._voluntarlyUsed = voluntarlyUsed
        self._virtual = self._voluntarlyUsed
        self._updateCharacteristicManager = updateCharacteristicManager

    @property
    def stepType(self) -> str:
        return "movementPointsVariation"

    @property
    def value(self) -> int:
        return self._intValue

    def start(self) -> None:
        if self._updateCharacteristicManager:
            FightEntitiesFrame.getCurrentInstance().setLastKnownEntityMovementPoint(
                self._targetId, -self._intValue, True
            )
        super().start()
