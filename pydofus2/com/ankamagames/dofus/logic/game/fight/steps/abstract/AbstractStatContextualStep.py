from whistle import Event
from com.ankamagames.berilia.types.event.BeriliaEvent import BeriliaEvent
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.types.characteristicContextual.CharacteristicContextual import (
    CharacteristicContextual,
)
from com.ankamagames.dofus.types.characteristicContextual.CharacteristicContextualManager import (
    CharacteristicContextualManager,
)
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.managers.OptionManager import OptionManager
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable

logger = Logger(__name__)


class AbstractStatContextualStep(AbstractSequencable):

    _color: int

    _value: str

    _targetId: float

    _blocking: bool

    _virtual: bool

    _ccm: CharacteristicContextual

    _gameContext: int

    def __init__(
        self,
        color: int,
        value: str,
        targetId: float,
        gameContext: int,
        blocking: bool = True,
    ):
        super().__init__()
        self._color = color
        self._value = value
        self._targetId = targetId
        self._gameContext = gameContext
        self._blocking = blocking

    def start(self) -> None:
        if (
            not self._virtual
            and self._value != "0"
            and OptionManager.getOptionManager("tiphon").getOption("pointsOverhead")
            != 0
        ):
            self._ccm = CharacteristicContextualManager().addStatContextual(
                self._value,
                DofusEntities.getEntity(self._targetId),
                TextFormat("Verdana", 24, self._color, True),
                OptionManager.getOptionManager("tiphon").getOption("pointsOverhead"),
                self._gameContext,
            )
        if not self._ccm:
            self.executeCallbacks()
            return
        if not self._blocking:
            self.executeCallbacks()
        else:
            self._ccm.addEventListener(BeriliaEvent.REMOVE_COMPONENT, self.remove)

    @property
    def target(self) -> IEntity:
        return DofusEntities.getEntity(self._targetId)

    @property
    def targets(self) -> list[float]:
        return [self._targetId]

    def remove(self, e: Event) -> None:
        self._ccm.removeEventListener(BeriliaEvent.REMOVE_COMPONENT, self.remove)
        self.executeCallbacks()
