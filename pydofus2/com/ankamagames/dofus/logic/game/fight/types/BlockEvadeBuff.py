from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import (
    CurrentPlayedFighterManager,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.fight.types.CastingSpell import CastingSpell
    from com.ankamagames.dofus.network.types.game.actions.fight.FightTemporaryBoostEffect import (
        FightTemporaryBoostEffect,
    )
    from com.ankamagames.dofus.logic.game.fight.frames.FightTurnFrame import (
        FightTurnFrame,
    )
from com.ankamagames.dofus.logic.game.fight.types.StatBuff import StatBuff


class BlockEvadeBuff(StatBuff):
    def __init__(
        self,
        effect: "FightTemporaryBoostEffect" = None,
        castingSpell: "CastingSpell" = None,
        actionId: int = 0,
    ):
        super().__init__(effect, castingSpell, actionId)

    def onApplied(self) -> None:
        super().onApplied()
        self.updateMovementPath()

    def onRemoved(self) -> None:
        super().onRemoved()
        self.updateMovementPath()

    def updateMovementPath(self) -> None:
        ftf: "FightTurnFrame" = Kernel().getWorker().getFrame("FightTurnFrame")
        if (
            self.targetId == CurrentPlayedFighterManager().currentFighterId
            and ftf
            and ftf.myTurn
            and ftf.lastPath
        ):
            ftf.updatePath()
