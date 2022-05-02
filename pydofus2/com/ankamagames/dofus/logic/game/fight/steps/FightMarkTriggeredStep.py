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

logger = Logger(__name__)


class FightMarkTriggeredStep(AbstractSequencable, IFightStep):

    _fighterId: float

    _casterId: float

    _markId: int

    def __init__(self, fighterId: float, casterId: float, markId: int):
        super().__init__()
        self._fighterId = fighterId
        self._casterId = casterId
        self._markId = markId

    @property
    def stepType(self) -> str:
        return "markTriggered"

    def start(self) -> None:
        mi: MarkInstance = MarkedCellsManager().getMarkDatas(self._markId)
        if not mi:
            logger.error(
                "Trying to trigger an unknown mark (" + self._markId + "). Aborting."
            )
            self.executeCallbacks()
            return
        evt: str = FightEventEnum.UNKNOWN_FIGHT_EVENT
        if mi.markType == GameActionMarkTypeEnum.GLYPH:
            evt = FightEventEnum.FIGHTER_TRIGGERED_GLYPH
        if mi.markType == GameActionMarkTypeEnum.TRAP:
            evt = FightEventEnum.FIGHTER_TRIGGERED_TRAP
        if mi.markType == GameActionMarkTypeEnum.PORTAL:
            evt = FightEventEnum.FIGHTER_TRIGGERED_PORTAL
        else:
            logger.warn("Unknown mark type triggered (" + str(mi.markType) + ").")
        FightEventsHelper().sendFightEvent(
            evt,
            [self._fighterId, self._casterId, mi.associatedSpell.id],
            0,
            self.castingSpellId,
        )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
