      
from pydofus2.com.ankamagames.dofus.datacenter.items.criterion import ItemCriterion
from pydofus2.com.ankamagames.jerakine.interfaces import IDataCenter
from pydofus2.com.ankamagames.dofus.datacenter.items.criterion import ItemCriterionOperator
from pydofus2.com.ankamagames.jerakine.data import I18n
from pydofus2.com.ankamagames.dofus.datacenter.items.criterion import IItemCriterion


class MariedItemCriterion(ItemCriterion, IDataCenter):
      
   
    def __init__(self, pCriterion:str):
        super().__init__(pCriterion)
   
    @property
    def text(self) -> str:
        readableCriterion:str = ""
        if self._operator.text == ItemCriterionOperator.EQUAL:
            if self._criterionValue == 1:
                readableCriterion = I18n.getUiText("ui.tooltip.beMaried")
            else:
                readableCriterion = I18n.getUiText("ui.tooltip.beSingle")
        elif self._operator.text == ItemCriterionOperator.DIFFERENT:
            if self._criterionValue == 2:
                readableCriterion = I18n.getUiText("ui.tooltip.beMaried")
            else:
                readableCriterion = I18n.getUiText("ui.tooltip.beSingle")
        return readableCriterion
   
    def clone(self) -> 'IItemCriterion':
        return MariedItemCriterion(self.basicText)

    def getCriterion(self) -> int:
        return 0
