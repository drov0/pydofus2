from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightStealingKamasStep(AbstractSequencable, IFightStep):

    _robberId: float

    _victimId: float

    _amount: float = 0

    def __init__(self, robberId: float, victimId: float, amount: float):
        super().__init__()
        self._robberId = robberId
        self._victimId = victimId
        self._amount = amount

    @property
    def stepType(self) -> str:
        return "stealingKamas"

    def start(self) -> None:
        FightEventsHelper().sendFightEvent(
            FightEventEnum.FIGHTER_STEALING_KAMAS,
            [self._robberId, self._victimId, self._amount],
            self._victimId,
            self.castingSpellId,
            False,
            3,
            2,
        )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._victimId]
