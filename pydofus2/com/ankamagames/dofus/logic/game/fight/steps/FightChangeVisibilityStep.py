from com.ankamagames.atouin.AtouinConstants import AtouinConstants
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.actions.RemoveEntityAction import (
    RemoveEntityAction,
)
from com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)

from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from com.ankamagames.dofus.logic.game.fight.miscs.FightEntitiesHolder import (
    FightEntitiesHolder,
)
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.logic.game.fight.types.FightEventEnum import FightEventEnum
from com.ankamagames.dofus.network.enums.GameActionFightInvisibilityStateEnum import (
    GameActionFightInvisibilityStateEnum,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from com.ankamagames.jerakine.entities.interfaces.IDisplayable import IDisplayable
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.fight.frames.FightContextFrame import (
        FightContextFrame,
    )


class FightChangeVisibilityStep(AbstractSequencable, IFightStep):

    _entityId: float

    _visibilityState: int

    _oldVisibilityState: int

    def __init__(self, entityId: float, visibilityState: int):
        super().__init__()
        fighterInfos: GameFightFighterInformations = FightEntitiesFrame.getCurrentInstance().getEntityInfos(entityId)
        self._oldVisibilityState = fighterInfos.stats.invisibilityState
        self._entityId = entityId
        self._visibilityState = visibilityState

    @property
    def stepType(self) -> str:
        return "changeVisibility"

    def start(self) -> None:
        if self._visibilityState == GameActionFightInvisibilityStateEnum.VISIBLE:
            invisibleEntity = self.respawnEntity()
            invisibleEntity.alpha = 1

            if isinstance(invisibleEntity, AnimatedCharacter):
                invisibleEntityPos = invisibleEntity.position
                entitiesFrame: FightEntitiesFrame = Kernel().getWorker().getFrame(FightEntitiesFrame)
                fightEntities = entitiesFrame.entities
                for entityId in fightEntities:
                    entityInfos = entitiesFrame.getEntityInfos(entityId)
                    if (
                        entitiesFrame.entityIsIllusion(entityId)
                        and entityInfos.stats.summoner == self._entityId
                        and entityInfos.disposition.cellId == invisibleEntityPos.cellId
                    ):
                        rea = RemoveEntityAction.create(entityId)
                        entitiesFrame.process(rea)

            if isinstance(invisibleEntity, AnimatedCharacter):
                invisibleEntity.canSeeThrough = False
                invisibleEntity.canWalkThrough = False
                invisibleEntity.canWalkTo = False

            if (
                self._oldVisibilityState == GameActionFightInvisibilityStateEnum.DETECTED
                or self._oldVisibilityState == GameActionFightInvisibilityStateEnum.INVISIBLE
            ):
                dispatchedState = GameActionFightInvisibilityStateEnum.VISIBLE

        elif self._visibilityState == GameActionFightInvisibilityStateEnum.DETECTED:
            if self._oldVisibilityState == GameActionFightInvisibilityStateEnum.VISIBLE:
                dispatchedState = GameActionFightInvisibilityStateEnum.INVISIBLE
            invisibleEntity = self.respawnEntity()

            if isinstance(invisibleEntity, AnimatedCharacter):
                invisibleEntity.canSeeThrough = True
                invisibleEntity.canWalkThrough = False
                invisibleEntity.canWalkTo = False
            invisibleEntity.alpha = 0.5

        elif self._visibilityState == GameActionFightInvisibilityStateEnum.INVISIBLE:
            if self._oldVisibilityState == GameActionFightInvisibilityStateEnum.VISIBLE:
                dispatchedState = GameActionFightInvisibilityStateEnum.INVISIBLE
            self.unspawnEntity()

        FightEventsHelper().sendFightEvent(
            FightEventEnum.FIGHTER_VISIBILITY_CHANGED,
            [self._entityId, dispatchedState],
            self._entityId,
            self.castingSpellId,
        )
        fcf: "FightContextFrame" = Kernel().getWorker().getFrame("FightContextFrame")
        if self._visibilityState == GameActionFightInvisibilityStateEnum.INVISIBLE:
            fcf.addToHiddenEntities(self._entityId)
        else:
            fcf.removeFromHiddenEntities(self._entityId)
        fighterInfos: GameFightFighterInformations = FightEntitiesFrame.getCurrentInstance().getEntityInfos(
            self._entityId
        )
        fighterInfos.stats.invisibilityState = self._visibilityState
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._entityId]

    def unspawnEntity(self) -> None:
        if FightEntitiesHolder().getEntity(self._entityId):
            return
        entity: IDisplayable = DofusEntities.getEntity(self._entityId)
        FightEntitiesHolder().holdEntity(entity)
        animatedEntity: AnimatedCharacter = entity
        if animatedEntity:
            animatedEntity.hide()

    def respawnEntity(self) -> IEntity:
        tiphonSprite = DofusEntities().getEntity(self._entityId)
        # if tiphonSprite and tiphonSprite.parentSprite:
        #     fightEntitiesFrame: "FightEntitiesFrame" = Kernel().getWorker().getFrame("FightEntitiesFrame")
        #     if fightEntitiesFrame:
        #         fightEntitiesFrame.addOrUpdateActor(fightEntitiesFrame.getEntityInfos(self._entityId))
        #     return tiphonSprite
        if FightEntitiesHolder().getEntity(self._entityId):
            FightEntitiesHolder().unholdEntity(self._entityId)
        return DofusEntities.getEntity(self._entityId)
