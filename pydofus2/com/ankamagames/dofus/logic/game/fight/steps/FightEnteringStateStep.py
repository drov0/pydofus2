from com.ankamagames.dofus.datacenter.spells.SpellState import SpellState
from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.BasicBuff import BasicBuff
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.dofus.logic.game.fight.types.StateBuff import StateBuff
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightEnteringStateStep(AbstractSequencable, IFightStep):

    _fighterId: float

    _stateId: int

    _durationString: str

    _buff: StateBuff

    def __init__(
        self, fighterId: float, stateId: int, durationString: str, buff: BasicBuff
    ):
        super().__init__()
        self._fighterId = fighterId
        self._stateId = stateId
        self._durationString = durationString
        self._buff = buff

    @property
    def stepType(self) -> str:
        return "enteringState"

    def start(self) -> None:
        spell: SpellState = SpellState.getSpellStateById(self._stateId)
        if spell and not spell.isSilent and self._buff.isVisibleInFightLog:
            FightEventsHelper().sendFightEvent(
                FightEventEnum.FIGHTER_ENTERING_STATE,
                [self._fighterId, self._stateId, self._durationString],
                self._fighterId,
                -1,
                False,
                2,
            )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
