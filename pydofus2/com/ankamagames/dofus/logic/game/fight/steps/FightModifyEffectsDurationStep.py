from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.managers.BuffManager import BuffManager
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightModifyEffectsDurationStep(AbstractSequencable, IFightStep):

    _sourceId: float

    _targetId: float

    _delta: int

    _virtualStep: IFightStep

    def __init__(self, sourceId: float, targetId: float, delta: int):
        super().__init__()
        self._sourceId = sourceId
        self._targetId = targetId
        self._delta = delta

    @property
    def stepType(self) -> str:
        return "modifyEffectsDuration"

    def start(self) -> None:
        BuffManager().incrementDuration(
            self._targetId, self._delta, True, BuffManager.INCREMENT_MODE_TARGET
        )
        FightEventsHelper().sendFightEvent(
            FightEventEnum.FIGHTER_EFFECTS_MODIFY_DURATION,
            [self._sourceId, self._targetId, self._delta],
            self._targetId,
            self.castingSpellId,
        )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._targetId]
