         
from pydofus2.com.ankamagames.dofus.datacenter.items.criterion import ItemCriterion
from pydofus2.com.ankamagames.jerakine.interfaces import IDataCenter
from pydofus2.com.ankamagames.dofus.logic.common.managers import PlayerManager
from pydofus2.com.ankamagames.dofus.datacenter.items.criterion import ItemCriterionOperator
from pydofus2.com.ankamagames.jerakine.data import I18n
from pydofus2.com.ankamagames.dofus.datacenter.items.criterion import IItemCriterion


class CommunityItemCriterion(ItemCriterion, IDataCenter):
      
   
    def __init__(self, pCriterion:str):
        super().__init__(pCriterion)

    @property
    def isRespected(self) -> bool:
        serverCommunity:int = PlayerManager().server.communityId
        if self._operator.text == ItemCriterionOperator.EQUAL:
            return serverCommunity == self.criterionValue
        elif self._operator.text == ItemCriterionOperator.DIFFERENT:
            return serverCommunity != self.criterionValue
        else:
            return False

    @property
    def text(self) -> str:
        readableCriterion:str = None
        readableCriterionValue:str = PlayerManager().server.community.name
        if self._operator.text == ItemCriterionOperator.EQUAL:
            readableCriterion = I18n.getUiText("ui.criterion.community",[readableCriterionValue])
        elif self._operator.text == ItemCriterionOperator.DIFFERENT:
            readableCriterion = I18n.getUiText("ui.criterion.notCommunity",[readableCriterionValue])
        return readableCriterion
   
    def clone(self) -> 'IItemCriterion':
        return CommunityItemCriterion(self.basicText)
