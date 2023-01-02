from pydofus2.com.ankamagames.dofus.logic.game.fight.steps.IFightStep import IFightStep
from pydofus2.com.ankamagames.dofus.network.enums.FightEventEnum import FightEventEnum
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.dofus.logic.game.fight.fightEvents.FightEventsHelper import (
    FightEventsHelper,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from pydofus2.com.ankamagames.dofus.logic.game.fight.frames.FightSpellCastFrame import (
    FightSpellCastFrame,
)

from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from pydofus2.com.ankamagames.jerakine.sequencer.AbstractSequencable import AbstractSequencable

logger = Logger("Dofus2")


class FightExchangePositionsStep(AbstractSequencable, IFightStep):

    _fighterOne: float

    _fighterOneNewCell: int

    _fighterTwo: float

    _fighterTwoNewCell: int

    _fighterOneVisibility: int

    def __init__(
        self,
        fighterOne: float,
        fighterOneNewCell: int,
        fighterTwo: float,
        fighterTwoNewCell: int,
    ):
        super().__init__()
        self._fighterOne = fighterOne
        self._fighterOneNewCell = fighterOneNewCell
        self._fighterTwo = fighterTwo
        self._fighterTwoNewCell = fighterTwoNewCell
        infos: "GameFightFighterInformations" = FightEntitiesFrame.getCurrentInstance().getEntityInfos(
            self._fighterOne
        )
        self._fighterOneVisibility = infos.stats.invisibilityState
        infos.disposition.cellId = self._fighterOneNewCell
        infos = FightEntitiesFrame.getCurrentInstance().getEntityInfos(self._fighterTwo)
        infos.disposition.cellId = self._fighterTwoNewCell

    @property
    def stepType(self) -> str:
        return "exchangePositions"

    def start(self) -> None:
        fighterInfosOne: GameFightFighterInformations = FightEntitiesFrame.getCurrentInstance().getEntityInfos(
            self._fighterOne
        )
        fighterInfosTwo: GameFightFighterInformations = FightEntitiesFrame.getCurrentInstance().getEntityInfos(
            self._fighterTwo
        )
        fighterInfosOne.disposition.cellId = self._fighterOneNewCell
        fighterInfosTwo.disposition.cellId = self._fighterTwoNewCell
        FightEventsHelper().sendFightEvent(
            FightEventEnum.FIGHTERS_POSITION_EXCHANGE,
            [self._fighterOne, self._fighterTwo],
            0,
            self.castingSpellId,
        )
        FightSpellCastFrame.updateRangeAndTarget()
        self.executeCallbacks()

    @property
    def targets(self) -> list[float]:
        return [self._fighterOne, self._fighterTwo]
