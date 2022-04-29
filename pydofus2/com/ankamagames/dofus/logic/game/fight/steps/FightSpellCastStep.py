from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.datacenter.spells.Spell import Spell
from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightSpellCastStep(AbstractSequencable, IFightStep):

    _fighterId: float

    _cellId: int

    _sourceCellId: int

    _spellId: int

    _spellRank: int

    _critical: int

    _portalIds: list[int]

    _verboseCast: bool

    def __init__(
        self,
        fighterId: float,
        cellId: int,
        sourceCellId: int,
        spellId: int,
        spellRank: int,
        critical: int,
        verboseCast: bool,
    ):
        super().__init__()
        self._fighterId = fighterId
        self._cellId = cellId
        self._sourceCellId = sourceCellId
        self._spellId = spellId
        self._spellRank = spellRank
        self._critical = critical
        self._verboseCast = verboseCast

    @property
    def stepType(self) -> str:
        return "spellCast"

    def start(self) -> None:
        if Spell.getSpellById(self._spellId).verbose_cast and self._verboseCast:
            FightEventsHelper.sendFightEvent(
                FightEventEnum.FIGHTER_CASTED_SPELL,
                [
                    self._fighterId,
                    self._cellId,
                    self._sourceCellId,
                    self._spellId,
                    self._spellRank,
                    self._critical,
                ],
                0,
                self.castingSpellId,
                False,
            )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
