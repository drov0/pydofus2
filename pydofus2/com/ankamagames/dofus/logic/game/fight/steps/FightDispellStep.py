from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.managers.BuffManager import BuffManager
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightDispellStep(AbstractSequencable, IFightStep):

    _fighterId: float

    def __init__(self, fighterId: float):
        super().__init__()
        self._fighterId = fighterId

    @property
    def stepType(self) -> str:
        return "dispell"

    def start(self) -> None:
        BuffManager().dispell(self._fighterId)
        FightEventsHelper().sendFightEvent(
            FightEventEnum.FIGHTER_GOT_DISPELLED,
            [self._fighterId],
            self._fighterId,
            self.castingSpellId,
        )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
