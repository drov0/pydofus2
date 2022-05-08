from com.ankamagames.dofus.datacenter.items.criterion.IItemCriterion import IItemCriterion
from com.ankamagames.dofus.datacenter.items.criterion.ItemCriterion import ItemCriterion
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter


class NumberOfMountBirthedCriterion(ItemCriterion, IDataCenter):
    def __init__(self, pCriterion: str):
        super().__init__(pCriterion)

    @property
    def text(self) -> str:
        readableCriterionValue: str = self._criterionValueText
        mountsBirthedCount: int = int(readableCriterionValue.split(",")[1]) + 1
        return I18n.getUiText("ui.mount.mountsBirthedCount", [mountsBirthedCount])

    def clone(self) -> IItemCriterion:
        return NumberOfMountBirthedCriterion(self.basicText)

    def getCriterion(self) -> int:
        return 0
