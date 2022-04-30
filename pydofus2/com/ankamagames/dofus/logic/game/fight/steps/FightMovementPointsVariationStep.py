from com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.steps.abstract.AbstractStatContextualStep import (
    AbstractStatContextualStep,
)
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.dofus.network.enums.GameContextEnum import GameContextEnum
from com.ankamagames.jerakine.utils.display.EnterFrameDispatcher import (
    EnterFrameDispatcher,
)


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
        EnterFrameDispatcher().worker.addSingleTreatment(StatsManager(), self.apply, [])

    def apply(self) -> None:
        if self._updateCharacteristicManager:
            FightEntitiesFrame.getCurrentInstance().setLastKnownEntityMovementPoint(
                self._targetId, -self._intValue, True
            )
        if self._showChatmessage:
            if self._intValue > 0:
                FightEventsHelper.sendFightEvent(
                    FightEventEnum.FIGHTER_MP_GAINED,
                    [self._targetId, abs(self._intValue)],
                    self._targetId,
                    self.castingSpellId,
                    False,
                    2,
                )
            elif self._intValue < 0:
                if self._voluntarlyUsed:
                    FightEventsHelper.sendFightEvent(
                        FightEventEnum.FIGHTER_MP_USED,
                        [self._targetId, abs(self._intValue)],
                        self._targetId,
                        self.castingSpellId,
                        False,
                        2,
                    )
                else:
                    FightEventsHelper.sendFightEvent(
                        FightEventEnum.FIGHTER_MP_LOST,
                        [self._targetId, abs(self._intValue)],
                        self._targetId,
                        self.castingSpellId,
                        False,
                        2,
                    )
        super().start()
