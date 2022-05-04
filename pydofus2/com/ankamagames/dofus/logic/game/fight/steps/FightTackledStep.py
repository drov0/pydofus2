from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from com.ankamagames.jerakine.sequencer.ISequencable import ISequencable
from com.ankamagames.jerakine.sequencer.ISequencableListener import ISequencableListener

logger = Logger(__name__)


class FightTackledStep(AbstractSequencable, IFightStep, ISequencableListener):

    _fighterId: float

    _animStep: ISequencable

    def __init__(self, fighterId: float):
        super().__init__()
        self._fighterId = fighterId

    @property
    def stepType(self) -> str:
        return "tackled"

    def start(self) -> None:
        tackledEntity: IEntity = DofusEntities.getEntity(self._fighterId)
        if not tackledEntity:
            logger.warn("Unable to play tackle of an unexisting fighter " + str(self._fighterId) + ".")
        self.stepFinished(self)

    def stepFinished(self, step: ISequencable, withTimout: bool = False) -> None:
        FightEventsHelper().sendFightEvent(
            FightEventEnum.FIGHTER_GOT_TACKLED,
            [self._fighterId],
            0,
            self.castingSpellId,
        )
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterId]
