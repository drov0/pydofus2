from pydofus2.com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from pydofus2.com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightKillStep(AbstractSequencable, IFightStep):

    _killerId: float

    _fighterId: float

    def __init__(self, fighterId: float, killerId: float):
        super().__init__()
        self._killerId = killerId
        self._fighterId = fighterId

    @property
    def stepType(self) -> str:
        return "kill"

    def start(self) -> None:
        FightEventsHelper().sendFightEvent(
            FightEventEnum.FIGHTER_GOT_KILLED,
            [self._killerId, self._fighterId],
            self._fighterId,
            self.castingSpellId,
        )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
