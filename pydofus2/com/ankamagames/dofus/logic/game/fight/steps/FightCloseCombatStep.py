from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.dofus.network.enums.FightSpellCastCriticalEnum import (
    FightSpellCastCriticalEnum,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from com.ankamagames.jerakine.sequencer.SerialSequencer import SerialSequencer


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
            FightEventsHelper.sendFightEvent(
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
