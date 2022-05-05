from com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
import com.ankamagames.dofus.logic.game.fight.managers.BuffManager as bffm
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from com.ankamagames.jerakine.sequencer.ISequencer import ISequencer
from com.ankamagames.jerakine.types.events.SequencerEvent import SequencerEvent
from damageCalculation.tools.StatIds import StatIds
from whistle import Event
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.fight.frames.FightBattleFrame import (
        FightBattleFrame,
    )

    from com.ankamagames.dofus.logic.game.fight.frames.FightContextFrame import (
        FightContextFrame,
    )
logger = Logger("pyd2bot")


class FightDeathStep(AbstractSequencable, IFightStep):

    _entityId: float = None

    _deathSubSequence: ISequencer = None

    _naturalDeath: bool = None

    _targetName: str = None

    _needToWarn: bool = True

    _timeOut: bool = False

    def __init__(self, entityId: float, naturalDeath: bool = True):
        super().__init__()
        self._entityId = entityId
        self._naturalDeath = naturalDeath
        fightContexteFrame: "FightContextFrame" = Kernel().getWorker().getFrame("FightContextFrame")
        if fightContexteFrame:
            self._targetName = fightContexteFrame.getFighterName(entityId)
        else:
            self._targetName = "???"

    @property
    def stepType(self) -> str:
        return "death"

    @property
    def entityId(self) -> float:
        return self._entityId

    def start(self) -> None:
        dyingEntity: IEntity = DofusEntities.getEntity(self._entityId)
        if not dyingEntity:
            logger.warn("Unable to play death of an unexisting fighter " + self._entityId + ".")
            self._needToWarn = True
            self.deathFinished()
            return
        fighterInfos: GameFightFighterInformations = FightEntitiesFrame.getCurrentInstance().getEntityInfos(
            self._entityId
        )
        fighterStats: EntityStats = StatsManager().getStats(fighterInfos.contextualId)
        fightBattleFrame: "FightBattleFrame" = Kernel().getWorker().getFrame("FightBattleFrame")
        if fightBattleFrame:
            fightBattleFrame.deadFightersList.append(self._entityId)
        self._needToWarn = True
        bffm.BuffManager().dispell(dyingEntity.id, False, False, True)
        bffm.BuffManager().removeLinkedBuff(dyingEntity.id, False, True)
        bffm.BuffManager().reaffectBuffs(dyingEntity.id)
        fighterStats.setStat(Stat(StatIds.CUR_PERMANENT_DAMAGE, 0))
        fighterStats.setStat(
            Stat(
                StatIds.CUR_LIFE,
                -(fighterStats.getMaxHealthPoints() + fighterStats.getStatTotalValue(StatIds.CUR_PERMANENT_DAMAGE)),
            )
        )
        self.deathFinished()

    def clear(self) -> None:
        if self._deathSubSequence:
            self._deathSubSequence.clear()
        super().clear()

    @property
    def targets(self) -> list[float]:
        return [self._entityId]

    def manualRollOut(self, fighterId: float) -> None:
        pass

    def onAnimEnd(self, dyingEntity) -> None:
        pass

    def deathTimeOut(self, e: Event = None) -> None:
        if self._deathSubSequence:
            self._deathSubSequence.removeEventListener(SequencerEvent.SEQUENCE_END, self.deathFinished)
            self._deathSubSequence.removeEventListener(SequencerEvent.SEQUENCE_TIMEOUT, self.deathTimeOut)
        self._timeOut = True

    def deathFinished(self, e: Event = None) -> None:
        if self._deathSubSequence:
            self._deathSubSequence.removeEventListener(SequencerEvent.SEQUENCE_END, self.deathFinished)
            self._deathSubSequence.removeEventListener(SequencerEvent.SEQUENCE_TIMEOUT, self.deathTimeOut)
            self._deathSubSequence = None
        if self._needToWarn:
            if self._naturalDeath:
                FightEventsHelper().sendFightEvent(
                    FightEventEnum.FIGHTER_DEATH,
                    [self._entityId, self._targetName],
                    self._entityId,
                    self.castingSpellId,
                    self._timeOut,
                )
            else:
                FightEventsHelper().sendFightEvent(
                    FightEventEnum.FIGHTER_LEAVE,
                    [self._entityId, self._targetName],
                    self._entityId,
                    self.castingSpellId,
                    self._timeOut,
                )
        self.executeCallbacks()
