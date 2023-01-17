from pydofus2.com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from pydofus2.com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from pydofus2.com.ankamagames.dofus.network.enums.FightSpellCastCriticalEnum import (
    FightSpellCastCriticalEnum,
)
from pydofus2.com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightCloseCombatStep(AbstractSequencable, IFightStep):

    _fighterId: float

    _weaponId: int

    _critical: int

    _verboseCast: bool

    def __init__(
        self, fighterId: float, weaponId: int, critical: int, verboseCast: bool
    ):
        super().__init__()
        self._fighterId = fighterId
        self._weaponId = weaponId
        self._critical = critical
        self._verboseCast = verboseCast

    @property
    def stepType(self) -> str:
        return "closeCombat"

    def start(self) -> None:
        if self._verboseCast:
            FightEventsHelper().sendFightEvent(
                FightEventEnum.FIGHTER_CLOSE_COMBAT,
                [self._fighterId, self._weaponId, self._critical],
                self._fighterId,
                self.castingSpellId,
                True,
            )
        if self._critical == FightSpellCastCriticalEnum.CRITICAL_HIT:
            pass
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
