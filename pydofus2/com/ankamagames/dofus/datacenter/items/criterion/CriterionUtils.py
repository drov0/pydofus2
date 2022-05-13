from com.ankamagames.dofus.datacenter.items.criterion.GroupItemCriterion import GroupItemCriterion
from com.ankamagames.dofus.datacenter.items.criterion.IItemCriterion import IItemCriterion
from com.ankamagames.dofus.datacenter.items.criterion.ItemCriterionFactory import ItemCriterionFactory
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from com.ankamagames.jerakine.utils.misc.StringUtils import StringUtils


class CriterionUtils(IDataCenter):
    @staticmethod
    def getCriteriaFromstr(pCriteriastrForm: str) -> list[IItemCriterion]:
        criteriastrForm: str = pCriteriastrForm
        criteria: list[IItemCriterion] = list[IItemCriterion]()
        if not criteriastrForm or len(criteriastrForm) == 0:
            return criteria
        tabParenthesis: list[str] = StringUtils.getDelimitedText(criteriastrForm, "(", ")", True)
        for stringCriterion in tabParenthesis:
            newGroupCriterion = GroupItemCriterion(stringCriterion)
            criteria.append(newGroupCriterion)
            criteriastrForm = str.replace(criteriastrForm, stringCriterion, "")
        tabSingleCriteria = criteriastrForm.split("[&|]")
        for stringCriterion2 in tabSingleCriteria:
            if stringCriterion2 != "":
                criteria.append(ItemCriterionFactory.create(stringCriterion2))
        return criteria
