from com.ankamagames.dofus.logic.game.fight.steps.FightDestroyEntityStep import (
    FightDestroyEntityStep,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.jerakine.logger.Logger import Logger
from whistle import Event
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from com.ankamagames.dofus.logic.game.fight.frames.FightSpellCastFrame import (
    FightSpellCastFrame,
)
from com.ankamagames.dofus.logic.game.fight.frames.FightTurnFrame import FightTurnFrame
from com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import (
    CurrentPlayedFighterManager,
)
from com.ankamagames.dofus.logic.game.fight.miscs.FightEntitiesHolder import (
    FightEntitiesHolder,
)
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.dofus.network.enums.GameActionFightInvisibilityStateEnum import (
    GameActionFightInvisibilityStateEnum,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from com.ankamagames.jerakine.sequencer.SerialSequencer import SerialSequencer
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint

logger = Logger("pyd2bot")


class FightThrowCharacterStep(AbstractSequencable, IFightStep):

    THROWING_PROJECTILE_FX: int = 21209

    _fighterId: float

    _carriedId: float

    _cellId: int

    _isCreature: bool

    portals: list[MapPoint]

    portalIds: list[int]

    def __init__(self, fighterId: float, carriedId: float, cellId: int):
        super().__init__()
        self._fighterId = fighterId
        self._carriedId = carriedId
        self._cellId = cellId
        self._isCreature = False

    @property
    def stepType(self) -> str:
        return "throwCharacter"

    def start(self) -> None:
        entitiesFrame: FightEntitiesFrame = Kernel().getWorker().getFrame(FightEntitiesFrame)
        carryingEntity = DofusEntities.getEntity(self._fighterId)
        carryingEntityInfos: GameFightFighterInformations = entitiesFrame.getEntityInfos(self._fighterId)
        carriedEntity: IEntity = DofusEntities.getEntity(self._carriedId)
        carriedEntityInfos: GameFightFighterInformations = entitiesFrame.getEntityInfos(self._carriedId)
        carryingFighterExist: bool = True
        if not carriedEntity or not carriedEntityInfos.spawnInfo.alive:
            logger.error(f"Attention, l'entit� [{self._fighterId}] ne porte pas [{self._carriedId}]")
            if carriedEntity:
                del carriedEntity
            self.throwFinished()
            return
        if not carryingEntity or not carryingEntityInfos.spawnInfo.alive:
            logger.error(f"Attention, l'entit� [{self._fighterId}] ne porte pas [{self._carriedId}]")
            carryingFighterExist = False
        fighterInfos: "GameFightFighterInformations" = FightEntitiesFrame.getCurrentInstance().getEntityInfos(
            self._carriedId
        )
        if self._cellId != -1:
            fighterInfos.disposition.cellId = self._cellId
        if self._carriedId == CurrentPlayedFighterManager().currentFighterId:
            fightTurnFrame: "FightTurnFrame" = Kernel().getWorker().getFrame("FightTurnFrame")
            if fightTurnFrame:
                fightTurnFrame.freePlayer()
        invisibility: bool = False
        if fighterInfos.stats.invisibilityState == GameActionFightInvisibilityStateEnum.INVISIBLE:
            invisibility = True
        logger.debug(f"{self._fighterId} is throwing {self._carriedId} (invisibility : {invisibility})")
        if not invisibility:
            FightEntitiesHolder().unholdEntity(self._carriedId)
        if carryingFighterExist:
            if self._cellId == -1 or invisibility:
                self.throwFinished()
                return
        finalTargetCell: MapPoint = MapPoint.fromCellId(self._cellId)
        if not invisibility:
            carriedEntity.position = finalTargetCell
        self.throwFinished()

    @property
    def targets(self) -> list[float]:
        return [self._carriedId]

    def throwFinished(self, e: Event = None) -> None:
        FightEventsHelper().sendFightEvent(
            FightEventEnum.FIGHTER_THROW,
            [self._fighterId, self._carriedId, self._cellId],
            0,
            self.castingSpellId,
        )
        FightSpellCastFrame.updateRangeAndTarget()
        self.executeCallbacks()

    def __str__(self) -> str:
        return f"[FightThrowCharacterStep(carrier={self._fighterId}, carried={self._carriedId}, cell={self._cellId})]"
