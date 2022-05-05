import json
from com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristic import (
    CharacterCharacteristic,
)
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable

logger = Logger("pyd2bot")


class FightUpdateStatStep(AbstractSequencable, IFightStep):

    STEP_TYPE: str = "updateStats"

    _entityId: float = None

    _newStats: list[CharacterCharacteristic] = None

    _targets: list[float] = None

    def __init__(self, entityId: float, newStats: list[CharacterCharacteristic]):
        super().__init__()
        self._entityId = entityId
        self._newStats = newStats
        self._targets = [self._entityId]

    @property
    def stepType(self) -> str:
        return self.STEP_TYPE

    @property
    def targets(self) -> list[float]:
        return self._targets

    def start(self) -> None:
        # logger.debug(f"new stats update*")
        # for stat in self._newStats:
        #     logger.debug(f"stat -> {json.dumps(stat.to_json(), indent=2)}")
        StatsManager().addRawStats(self._entityId, self._newStats)
        super().start()
        self.executeCallbacks()
