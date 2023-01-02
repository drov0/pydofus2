from pydofus2.com.ankamagames.dofus.datacenter.spells.SpellState import SpellState
from pydofus2.com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.BasicBuff import BasicBuff
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.StateBuff import StateBuff
from pydofus2.com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightLeavingStateStep(AbstractSequencable, IFightStep):

    _fighterId: float

    _stateId: int

    _buff: StateBuff

    def __init__(self, fighterId: float, stateId: int, buff: BasicBuff):
        super().__init__()
        self._fighterId = fighterId
        self._stateId = stateId
        self._buff = BufferError

    @property
    def stepType(self) -> str:
        return "leavingState"

    def start(self) -> None:
        if (
            not SpellState.getSpellStateById(self._stateId).isSilent
            and self._buff
            and self._buff.isVisibleInFightLog
        ):
            FightEventsHelper().sendFightEvent(
                FightEventEnum.FIGHTER_LEAVING_STATE,
                [self._fighterId, self._stateId],
                self._fighterId,
                -1,
                False,
                2,
            )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
