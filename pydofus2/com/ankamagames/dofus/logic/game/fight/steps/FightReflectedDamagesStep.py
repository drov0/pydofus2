from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightReflectedDamagesStep(AbstractSequencable, IFightStep):

    _fighterId: float

    def __init__(self, fighterId: float):
        super().__init__()
        self._fighterId = fighterId

    @property
    def stepType(self) -> str:
        return "reflectedDamages"

    def start(self) -> None:
        FightEventsHelper.sendFightEvent(
            FightEventEnum.FIGHTER_REFLECTED_DAMAGES,
            [self._fighterId],
            self._fighterId,
            self.castingSpellId,
        )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
