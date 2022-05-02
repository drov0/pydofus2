from time import perf_counter
from com.ankamagames.dofus.datacenter.spells.Spell import Spell
from com.ankamagames.dofus.datacenter.spells.SpellLevel import SpellLevel
from com.ankamagames.dofus.logic.game.common.misc.ISpellCastProvider import (
    ISpellCastProvider,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from com.ankamagames.jerakine.types.Callback import Callback

logger = Logger(__name__)


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
                "Executing SpellScript"
                + str(self._fxScriptId)
                + " for spell '"
                + self._spellCastProvider.castingSpell.spell.name
                + "' ("
                + str(self._spellCastProvider.castingSpell.spell.id)
                + ")"
            )
        logger.debug("Script successfuly executed")

    @property
    def stepType(self) -> str:
        return "spellCast"

    def start(self) -> None:
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
