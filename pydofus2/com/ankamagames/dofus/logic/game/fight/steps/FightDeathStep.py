import pydofus2.com.ankamagames.dofus.logic.game.fight.managers.BuffManager as bffm
from pydofus2.com.ankamagames.atouin.managers.EntitiesManager import \
    EntitiesManager
from pydofus2.com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.logic.common.managers.StatsManager import \
    StatsManager
from pydofus2.com.ankamagames.dofus.logic.game.common.misc.DofusEntities import \
    DofusEntities
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import \
    IFightStep
from pydofus2.com.ankamagames.jerakine.entities.interfaces.IEntity import \
    IEntity
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.sequencer.AbstractSequencable import \
    AbstractSequencable
from pydofus2.damageCalculation.tools.StatIds import StatIds


class FightDeathStep(AbstractSequencable, IFightStep):

    _entityId: float = None

    _naturalDeath: bool = None

    _targetName: str = None

    def __init__(self, entityId: float, naturalDeath: bool = True):
        super().__init__()
        self._entityId = entityId
        self._naturalDeath = naturalDeath
        fightContexteFrame = Kernel().fightContextFrame
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
        dyingEntity: IEntity = DofusEntities().getEntity(self._entityId)
        if not dyingEntity:
            return
        fightEntitites = Kernel().fightEntitiesFrame
        fighterInfos = fightEntitites.getEntityInfos(self._entityId)
        fighterStats = StatsManager().getStats(fighterInfos.contextualId)
        fightBattleFrame = Kernel().battleFrame
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
        del fighterInfos
        del fightEntitites.entities[self._entityId]
        EntitiesManager().removeEntity(self._entityId)
        Logger().info(f"[FightSequence] Fighter {self._entityId} died")
        self.executeCallbacks()

    def clear(self) -> None:
        super().clear()

    @property
    def targets(self) -> list[float]:
        return [self._entityId]
