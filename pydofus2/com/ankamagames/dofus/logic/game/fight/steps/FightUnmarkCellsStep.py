from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.managers.MarkedCellsManager import (
    MarkedCellsManager,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.dofus.logic.game.fight.types.MarkInstance import MarkInstance
from com.ankamagames.dofus.network.enums.GameActionMarkTypeEnum import (
    GameActionMarkTypeEnum,
)
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable

logger = Logger("pyd2bot")


class FightUnmarkCellsStep(AbstractSequencable, IFightStep):

    _markId: int

    def __init__(self, markId: int):
        super().__init__()
        self._markId = markId

    @property
    def stepType(self) -> str:
        return "unmarkCells"

    def start(self) -> None:
        mi: MarkInstance = MarkedCellsManager().getMarkDatas(self._markId)
        if not mi:
            logger.error("Trying to remove an unknown mark (" + str(self._markId) + "). Aborting.")
            self.executeCallbacks()
            return
        MarkedCellsManager().removeGlyph(self._markId)
        evt: str = FightEventEnum.UNKNOWN_FIGHT_EVENT
        if mi.markType == GameActionMarkTypeEnum.GLYPH:
            evt = FightEventEnum.GLYPH_DISAPPEARED
        elif mi.markType == GameActionMarkTypeEnum.TRAP:
            evt = FightEventEnum.TRAP_DISAPPEARED
        elif mi.markType == GameActionMarkTypeEnum.PORTAL:
            evt = FightEventEnum.PORTAL_DISAPPEARED
        elif mi.markType == GameActionMarkTypeEnum.RUNE:
            evt = FightEventEnum.RUNE_DISAPPEARED
        elif mi.markType == GameActionMarkTypeEnum.WALL:
            pass
        else:
            logger.warn("Unknown mark type (" + mi.markType + ").")
        FightEventsHelper().sendFightEvent(evt, [mi.associatedSpell.id], 0, self.castingSpellId)
        MarkedCellsManager().removeMark(self._markId)
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._markId]
