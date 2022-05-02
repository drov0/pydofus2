from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightReducedDamagesStep(AbstractSequencable, IFightStep):

    _fighterId: float

    _amount: int

    def __init__(self, fighterId: float, amount: int):
        super().__init__()
        self._fighterId = fighterId
        self._amount = amount

    @property
    def stepType(self) -> str:
        return "reducedDamages"

    def start(self) -> None:
        FightEventsHelper().sendFightEvent(
            FightEventEnum.FIGHTER_REDUCED_DAMAGES,
            [self._fighterId, self._amount],
            self._fighterId,
            self.castingSpellId,
        )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
