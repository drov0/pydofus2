from typing import TYPE_CHECKING

import com.ankamagames.dofus.logic.game.fight.managers.BuffManager as bffm
from com.ankamagames.atouin.managers.EntitiesManager import EntitiesManager
from com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import FightEntitiesFrame
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from damageCalculation.tools.StatIds import StatIds

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.fight.frames.FightBattleFrame import FightBattleFrame
    from com.ankamagames.dofus.logic.game.fight.frames.FightContextFrame import FightContextFrame
logger = Logger("Dofus2")


class FightDeathStep(AbstractSequencable, IFightStep):

    _entityId: float = None

    _naturalDeath: bool = None

    _targetName: str = None

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
        logger.debug("??????????????? FightDeathStep start")
        dyingEntity: IEntity = DofusEntities.getEntity(self._entityId)
        if not dyingEntity:
            logger.warn("Unable to play death of an unexisting fighter " + self._entityId + ".")
            return
        fightEntitites = FightEntitiesFrame.getCurrentInstance()
        fighterInfos: GameFightFighterInformations = fightEntitites.getEntityInfos(self._entityId)
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
        del fighterInfos
        del fightEntitites.entities[self._entityId]
        EntitiesManager().removeEntity(self._entityId)
        self.executeCallbacks()

    def clear(self) -> None:
        super().clear()

    @property
    def targets(self) -> list[float]:
        return [self._entityId]
