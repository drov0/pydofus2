from time import perf_counter
from pydofus2.com.ankamagames.dofus.datacenter.spells.Spell import Spell
from pydofus2.com.ankamagames.dofus.datacenter.spells.SpellLevel import SpellLevel
from pydofus2.com.ankamagames.dofus.logic.game.common.misc.ISpellCastProvider import (
    ISpellCastProvider,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from pydofus2.com.ankamagames.jerakine.types.Callback import Callback

logger = Logger("Dofus2")


class FightPlaySpellScriptStep(AbstractSequencable, IFightStep):

    _fighterId: float

    _cellId: int

    _spellId: int

    _spellRank: int

    _portalIds: list[int]

    _fxScriptId: int

    _scriptStarted: int

    _spellCastProvider: ISpellCastProvider

    def __init__(
        self,
        fxScriptId: int,
        fighterId: float,
        cellId: int,
        spellId: int,
        spellRank: int,
        spellCastProvider: ISpellCastProvider,
    ):
        super().__init__()
        self._fxScriptId = fxScriptId
        self._spellId = spellId
        self._spellRank = spellRank
        self._spellCastProvider = spellCastProvider
        self._fighterId = fighterId
        if self._fxScriptId == 0:
            return
        s: Spell = Spell.getSpellById(self._spellId)
        if not s:
            return
        sl: SpellLevel = s.getSpellLevel(self._spellRank)
        if not sl or not sl.playAnimation:
            return
        if self._spellCastProvider.castingSpell.spell:
            logger.info(
                "Executing Spell "
                + self._spellCastProvider.castingSpell.spell.name
                + "' ("
                + str(self._spellCastProvider.castingSpell.spell.id)
                + ")"
            )
        # logger.debug("Script successfuly executed")

    @property
    def stepType(self) -> str:
        return "spellCast"

    def start(self) -> None:
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
