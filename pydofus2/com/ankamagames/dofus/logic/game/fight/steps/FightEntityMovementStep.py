from typing import TYPE_CHECKING

from pydofus2.com.ankamagames.atouin.managers.EntitiesManager import \
    EntitiesManager
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import (
    KernelEvent, KernelEventsManager)
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.logic.game.common.misc.DofusEntities import \
    DofusEntities
from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import \
    FightEntitiesFrame
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import \
    IFightStep
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.sequencer.AbstractSequencable import \
    AbstractSequencable

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightContextFrame import \
        FightContextFrame
    from pydofus2.com.ankamagames.dofus.types.entities.AnimatedCharacter import \
        AnimatedCharacter
    from pydofus2.com.ankamagames.jerakine.types.positions.MovementPath import \
        MovementPath


class FightEntityMovementStep(AbstractSequencable, IFightStep):

    _entityId: float

    _entity: "AnimatedCharacter"

    _path: "MovementPath"

    _fightContextFrame: "FightContextFrame"

    _ttCacheName: str

    _ttName: str

    def __init__(self, entityId: float, path: "MovementPath"):
        super().__init__()
        self._entityId = entityId
        self._path = path
        self.timeout = len(path)
        self._fightContextFrame: "FightContextFrame" = Kernel().worker.getFrameByName("FightContextFrame")

    @property
    def stepType(self) -> str:
        return "entityMovement"

    def start(self) -> None:
        self._entity = DofusEntities().getEntity(self._entityId)
        if self._entity:
            self._entity.position.cellId = self._path.end.cellId
            fighterInfos = FightEntitiesFrame.getCurrentInstance().getEntityInfos(self._entityId)
            fighterInfos.disposition.cellId = self._path.end.cellId
            for e in EntitiesManager().getEntitiesOnCell(self._path.end.cellId):
                if e.id != self._entityId:
                    Logger().error("Placed the wrong entity on cell")
            KernelEventsManager().send(KernelEvent.FIGHTER_MOVEMENT_APPLIED, self._entityId, self._path)
        else:
            Logger().warn(f"Unable to move unknown entity {self._entityId}.")
        self.movementEnd()

    @property
    def targets(self) -> list[float]:
        return [self._entityId]

    def updateCarriedEntitiesPosition(self) -> None:
        entitiesFrame: "FightEntitiesFrame" = Kernel().worker.getFrameByName("FightEntitiesFrame")
        carriedEntity: "AnimatedCharacter" = self._entity.carriedEntity
        while carriedEntity:
            infos = entitiesFrame.getEntityInfos(carriedEntity.id)
            if infos and carriedEntity.position.cellId != -1:
                infos.disposition.cellId = self._entity.position.cellId
            carriedEntity = carriedEntity.carriedEntity

    def movementEnd(self) -> None:
        self.updateCarriedEntitiesPosition()
        self.executeCallbacks()
