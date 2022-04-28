from com.ankamagames.dofus.datacenter.items.criterion.IItemCriterion import (
    IItemCriterion,
)
from com.ankamagames.dofus.datacenter.items.criterion.ItemCriterion import ItemCriterion
from com.ankamagames.dofus.datacenter.items.criterion.ItemCriterionOperator import (
    ItemCriterionOperator,
)
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter


class FriendlistItemCriterion(ItemCriterion, IDataCenter):
    def __init__(self, pCriterion: str):
        super().__init__(pCriterion)

    @property
    def text(self) -> str:
        readableCriterionRef: str = I18n.getUiText("ui.tooltip.playerInFriendlist")
        readableOperator: str = self._operator.text
        if readableOperator == ItemCriterionOperator.EQUAL:
            readableOperator = ":"
        return (
            readableCriterionRef + " " + readableOperator + " " + self._criterionValue
        )

    def clone(self) -> IItemCriterion:
        return FriendlistItemCriterion(self.basicText)

    def getCriterion(self) -> int:
        return Kernel().getWorker().getFrame("SocialFrame")
