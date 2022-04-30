from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from typing import TYPE_CHECKING
from com.ankamagames.jerakine.logger.Logger import Logger

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.fight.frames.FightContextFrame import (
        FightContextFrame,
    )
    from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
        FightEntitiesFrame,
    )
    from com.ankamagames.dofus.logic.game.fight.frames.FightSpellCastFrame import (
        FightSpellCastFrame,
    )
    from com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
    from com.ankamagames.jerakine.sequencer.AbstractSequencable import (
        AbstractSequencable,
    )
    from com.ankamagames.jerakine.types.positions.MovementPath import MovementPath

logger = Logger(__name__)


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
        self._fightContextFrame: "FightContextFrame" = (
            Kernel().getWorker().getFrame("FightContextFrame")
        )

    @property
    def stepType(self) -> str:
        return "entityMovement"

    def start(self) -> None:
        self._entity = DofusEntities.getEntity(self._entityId)
        if self._entity:
            fighterInfos = FightEntitiesFrame.getCurrentInstance().getEntityInfos(
                self._entityId
            )
            fighterInfos.disposition.cellId = self._path.end.cellId
        else:
            logger.warn(f"Unable to move unknown entity {self._entityId}.")
        self.movementEnd()

    @property
    def targets(self) -> list[float]:
        return [self._entityId]

    def updateCarriedEntitiesPosition(self) -> None:
        entitiesFrame: "FightEntitiesFrame" = (
            Kernel().getWorker().getFrame("FightEntitiesFrame")
        )
        carriedEntity: "AnimatedCharacter" = self._entity.carriedEntity
        while carriedEntity:
            infos = entitiesFrame.getEntityInfos(carriedEntity.id)
            if infos and carriedEntity.position.cellId != -1:
                infos.disposition.cellId = self._entity.position.cellId
            carriedEntity = carriedEntity.carriedEntity

    def movementEnd(self) -> None:
        self.updateCarriedEntitiesPosition()
        FightSpellCastFrame.updateRangeAndTarget()
        self.executeCallbacks()
