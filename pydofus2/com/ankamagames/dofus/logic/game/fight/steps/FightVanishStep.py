from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.managers.BuffManager import BuffManager
from com.ankamagames.dofus.logic.game.fight.miscs.FightEntitiesHolder import (
    FightEntitiesHolder,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from com.ankamagames.jerakine.sequencer.ISequencer import ISequencer

logger = Logger("pyd2bot")


class FightVanishStep(AbstractSequencable, IFightStep):

    _entityId: float

    _sourceId: float

    _vanishSubSequence: ISequencer

    def __init__(self, entityId: float, sourceId: float):
        super().__init__()
        self._entityId = entityId
        self._sourceId = sourceId

    @property
    def stepType(self) -> str:
        return "vanish"

    @property
    def entityId(self) -> float:
        return self._entityId

    def start(self) -> None:
        vanishingEntity: IEntity = DofusEntities.getEntity(self._entityId)
        if not vanishingEntity:
            logger.warn("Unable to play vanish of an unexisting fighter " + str(self._entityId) + ".")
            self.executeCallbacks()
            return
        BuffManager().dispell(vanishingEntity.id, False, False, True)
        BuffManager().removeLinkedBuff(vanishingEntity.id, False, True)
        BuffManager().reaffectBuffs(vanishingEntity.id)
        FightEntitiesHolder().unholdEntity(vanishingEntity.id)
        self.executeCallbacks()

    def clear(self) -> None:
        if self._vanishSubSequence:
            self._vanishSubSequence.clear()
        super().clear()

    @property
    def targets(self) -> list[float]:
        return [self._entityId]
