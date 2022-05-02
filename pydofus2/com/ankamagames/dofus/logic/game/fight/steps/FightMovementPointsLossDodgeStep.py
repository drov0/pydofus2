from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.steps.abstract.AbstractDodgePointLossStep import (
    AbstractDodgePointLossStep,
)
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum


class FightMovementPointsLossDodgeStep(AbstractDodgePointLossStep, IFightStep):
    def __init__(self, fighterId: float, amount: int):
        super().__init__(fighterId, amount)

    @property
    def stepType(self) -> str:
        return "movementPointsLossDodge"

    def start(self) -> None:
        FightEventsHelper().sendFightEvent(
            FightEventEnum.FIGHTER_MP_LOSS_DODGED,
            [self.fighterId, self._amount],
            self._fighterId,
            self.castingSpellId,
        )
        self.executeCallbacks()
