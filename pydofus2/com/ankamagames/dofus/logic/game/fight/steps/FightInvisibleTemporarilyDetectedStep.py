from pydofus2.com.ankamagames.atouin.managers.EntitiesManager import EntitiesManager
from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from pydofus2.com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from pydofus2.com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable


class FightInvisibleTemporarilyDetectedStep(AbstractSequencable, IFightStep):

    _duplicateSprite: AnimatedCharacter

    _cellId: int

    _targetId: float

    def __init__(self, target: AnimatedCharacter, cellId: int):
        super().__init__()
        self._targetId = target.id
        id: float = EntitiesManager().getFreeEntityId()
        self._duplicateSprite = AnimatedCharacter(id)
        self._cellId = cellId

    @property
    def stepType(self) -> str:
        return "invisibleTemporarilyDetected"

    def start(self) -> None:
        self.executeCallbacks()

    def clear(self) -> None:
        pass

    @property
    def targets(self) -> list[float]:
        return [self._targetId]

    def onFade(self, e) -> None:
        pass
