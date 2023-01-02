from pydofus2.com.ankamagames.dofus import datacenter
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.datacenter.items.criterion.IItemCriterion import (
        IItemCriterion,
    )
import pydofus2.com.ankamagames.dofus.datacenter.items.criterion.ItemCriterionFactory as icFactory
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from pydofus2.com.ankamagames.dofus.network.types.game.character.alignment.ActorExtendedAlignmentInformations import (
    ActorExtendedAlignmentInformations,
)
from pydofus2.com.ankamagames.jerakine.data.I18n import I18n


class AlignmentLevelItemCriterion(icFactory.ItemCriterionFactory, datacenter):
    def __init__(self, pCriterion: str):
        super().__init__(pCriterion)

    @property
    def text(self) -> str:
        readableCriterionRef: str = I18n.getUiText("ui.tooltip.AlignmentLevel")
        return (
            readableCriterionRef
            + " "
            + self._operator.text
            + " "
            + self._criterionValue
        )

    def clone(self) -> IItemCriterion:
        return AlignmentLevelItemCriterion(self.basicText)

    def getCriterion(self) -> int:
        alignInfo: ActorExtendedAlignmentInformations = (
            PlayedCharacterManager().characteristics.alignmentInfos
        )
        return alignInfo.alignmentValue
