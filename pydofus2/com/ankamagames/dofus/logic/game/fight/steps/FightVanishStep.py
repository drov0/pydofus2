from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.frames.FightBattleFrame import (
    FightBattleFrame,
)
from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from com.ankamagames.dofus.logic.game.fight.managers.BuffManager import BuffManager
from com.ankamagames.dofus.logic.game.fight.steps.FightDestroyEntityStep import (
    FightDestroyEntityStep,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.jerakine.logger.Logger import Logger
from whistle import Event
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from com.ankamagames.jerakine.sequencer.CallbackStep import CallbackStep
from com.ankamagames.jerakine.sequencer.ISequencer import ISequencer
from com.ankamagames.jerakine.sequencer.SerialSequencer import SerialSequencer
from com.ankamagames.jerakine.types.Callback import Callback
from com.ankamagames.jerakine.types.events.SequencerEvent import SequencerEvent

logger = Logger(__name__)


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
        myPos: int = 0
        vanishingEntity: IEntity = DofusEntities.getEntity(self._entityId)
        if not vanishingEntity:
            logger.warn(
                "Unable to play vanish of an unexisting fighter "
                + str(self._entityId)
                + "."
            )
            self.vanishFinished()
            return
        BuffManager().dispell(vanishingEntity.id, False, False, True)
        impactedTarget = BuffManager().removeLinkedBuff(vanishingEntity.id, False, True)
        BuffManager().reaffectBuffs(vanishingEntity.id)
        self._vanishSubSequence = SerialSequencer(FightBattleFrame.FIGHT_SEQUENCER_NAME)
        myPos = (
            FightEntitiesFrame.getCurrentInstance()
            .getEntityInfos(self._sourceId)
            .disposition.cellId
        )
        if vanishingEntity.position.cellId != myPos:
            self._vanishSubSequence.addStep(
                CallbackStep(Callback(self.onAnimEnd, vanishingEntity))
            )
        self._vanishSubSequence.addStep(
            CallbackStep(Callback(self.manualRollOut, self._entityId))
        )
        self._vanishSubSequence.addStep(FightDestroyEntityStep(vanishingEntity))
        self._vanishSubSequence.add_listener(
            SequencerEvent.SEQUENCE_END, self.vanishFinished
        )
        self._vanishSubSequence.start()

    def clear(self) -> None:
        if self._vanishSubSequence:
            self._vanishSubSequence.clear()
        super().clear()

    @property
    def targets(self) -> list[float]:
        return [self._entityId]

    def manualRollOut(self, fighterId: float) -> None:
        pass

    def onAnimEnd(self, vanishingEntity) -> None:
        pass

    def vanishFinished(self, e: Event = None) -> None:
        if self._vanishSubSequence:
            self._vanishSubSequence.remove_listener(
                SequencerEvent.SEQUENCE_END, self.vanishFinished
            )
            self._vanishSubSequence = None
        self.executeCallbacks()
