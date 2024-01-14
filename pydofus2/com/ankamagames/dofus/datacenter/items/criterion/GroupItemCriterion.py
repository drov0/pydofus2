from pydofus2.com.ankamagames.dofus.datacenter.items.criterion.IItemCriterion import \
    IItemCriterion
from pydofus2.com.ankamagames.dofus.datacenter.items.criterion.ItemCriterion import \
    ItemCriterion
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
    PlayedCharacterManager
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.utils.misc.StringUtils import \
    StringUtils


class GroupItemCriterion(IItemCriterion):

    _criteria: list[ItemCriterion]
    _operators: list[str]
    _criterionTextForm: str
    _cleanCriterionTextForm: str
    _malformated: bool
    _singleOperatorType: bool

    def __init__(self, pCriterion: str):
        super().__init__()
        self._criterionTextForm = pCriterion
        self._cleanCriterionTextForm = self._criterionTextForm[:]
        self._malformated = False
        self._singleOperatorType = False
        if not pCriterion:
            return
        self.parse()
        # self.createNewGroups()

    @classmethod
    def create(cls, pCriteria: list[ItemCriterion], pOperators: list[str]) -> "GroupItemCriterion":
        textForm = ""
        criterionIndex = 0
        operatorIndex = 0
        tabLength = len(pCriteria) + len(pOperators)

        for i in range(tabLength):
            if i % 2 == 0:
                textForm += pCriteria[criterionIndex].basicText
                criterionIndex += 1
            else:
                textForm += pOperators[operatorIndex]
                operatorIndex += 1

        return GroupItemCriterion(textForm)

    @property
    def criteria(self) -> list[ItemCriterion]:
        return self._criteria

    @property
    def inlineCriteria(self) -> list[ItemCriterion]:
        criteria = list[ItemCriterion]()
        for criterion in self._criteria:
            criteria = criteria.extend(criterion.inlineCriteria)
        return criteria

    @property
    def isRespected(self) -> bool:
        if not self._criteria:
            return True
        
        player = PlayedCharacterManager()
        
        if not player or not player.characteristics:
            Logger().error("Character or characteristics doesn't exist !, returning true")
            return True
        
        if self._criteria and len(self._criteria) == 1 and isinstance(self._criteria[0], ItemCriterion):
            return self._criteria[0].isRespected
        
        if len(self._operators) > 0 and self._operators[0] == "|":
            for criterion in self._criteria:
                if criterion.isRespected:
                    return True
            return False
        
        for criterion in self._criteria:
            if not criterion.isRespected:
                return False
            
        return True

    @property
    def text(self) -> str:
        textForm = ""
        if not self._criteria:
            return textForm
        tabLength = len(self._criteria) + len(self._operators)
        criterionIndex = 0
        operatorIndex = 0
        for i in range(tabLength):
            if textForm:
                textForm += " "
            if i % 2 == 0:
                textForm += self._criteria[criterionIndex].text
                criterionIndex += 1
            else:
                textForm += self._operators[operatorIndex]
                operatorIndex += 1
        return textForm

    @property
    def basicText(self) -> str:
        return self._criterionTextForm

    def clone(self) -> IItemCriterion:
        return GroupItemCriterion(self.basicText)

    def createNewGroups(self) -> None:
        if self._malformated or not self._criteria or len(self._criteria) <= 2 or self._singleOperatorType:
            return
        copyCriteria = list[ItemCriterion]()
        copyOperators = list[str]()
        for crit in self._criteria:
            copyCriteria.append(crit.clone())
        for ope in self._operators:
            copyOperators.append(ope)
        curIndex = 0
        while True:
            if len(copyCriteria) <= 2:
                break
            else:
                crits = list[IItemCriterion]()
                if copyOperators[curIndex] == "&":
                    crits.append(copyCriteria[curIndex])
                    crits.append(copyCriteria[curIndex + 1])
                    ops = [copyOperators[curIndex]]
                    group = GroupItemCriterion.create(crits, ops)
                    copyCriteria[curIndex:curIndex + 2] = [group]
                    del copyOperators[curIndex]
                    curIndex -= 1
                curIndex += 1
                if curIndex >= len(copyOperators):
                    break
        self._criteria = copyCriteria
        self._operators = copyOperators
        self._singleOperatorType = self.checkSingleOperatorType(self._operators)

    def remove_criterion_from_string(self, string, criterion):
        index = string.index(criterion.basicText)
        return string[:index] + string[index + len(criterion.basicText):]
    
    def find_next_operator_index(self, string):
        for operator in ["&", "|"]:
            index = string.find(operator)
            if index != -1:
                return index
        return -1

    def parse(self) -> None:
        self._criteria = list[ItemCriterion]()
        self._operators = list[str]()
        searchingstr = str.replace(searchingstr, " ", "")
        delimitedlist = StringUtils.getDelimitedText(searchingstr, "(", ")", True)
        if len(delimitedlist) > 0 and delimitedlist[0] == searchingstr:
            searchingstr = searchingstr[1:-1]
        if not searchingstr:
            return
        self._singleOperatorType = self.checkSingleOperatorType(self._operators)
        while searchingstr:
            criterion = self.getFirstCriterion(searchingstr)
            if criterion:
                self._criteria.append(criterion)
                searchingstr = self.remove_criterion_from_string(searchingstr, criterion)
                if not searchingstr:
                    break
                operator = searchingstr[:1]
                self._operators.append(operator)
                searchingstr = searchingstr[1:]
            else:
                operator_index = self.find_next_operator_index(searchingstr)
                if operator_index == -1:
                    break
                searchingstr = searchingstr[operator_index + 1:]
        if self._operators and self._criteria and len(self._operators) >= len(self._criteria):
            Logger().error("Malformated criterion found !")
            self._malformated = True

    def getFirstCriterion(self, pCriteria: str) -> ItemCriterion:
        if not pCriteria:
            return None
        
        pCriteria = pCriteria.replace(" ", "")
        
        if pCriteria.startswith("("):
            dl = StringUtils.getDelimitedText(pCriteria, "(", ")", True)
            return GroupItemCriterion(dl[0])

        else:
            ANDindex = pCriteria.find("&")
            ORindex = pCriteria.find("|")
            
            from pydofus2.com.ankamagames.dofus.datacenter.items.criterion.ItemCriterionFactory import \
                ItemCriterionFactory

            if ANDindex == -1 and ORindex == -1: # No operators
                firstCriterion = pCriteria
                
            elif ANDindex != -1 and (ANDindex < ORindex or ORindex == -1): # AND operator first or no OR operators
                firstCriterion = pCriteria.split("&")[0]
                
            else: # OR operator first or no AND operator
                firstCriterion = pCriteria.split("|")[0]

            return ItemCriterionFactory.create(firstCriterion) 

    def checkSingleOperatorType(self, pOperators: list[str]) -> bool:
        for op in pOperators:
            if op != pOperators[0]:
                return False
        return True

    @property
    def operators(self) -> list[str]:
        return self._operators
    
    def __repr__(self):
        return self.text

if __name__ == "__main__":
    cr = GroupItemCriterion('(((Qo>3613&PO<11044,1&Qo<3597)&(Qo>3617&Qo<3600))&CE>0)')
    # cr = GroupItemCriterion('Qo>3613&PO<11044,1&Qo<3597')
    print(cr)
    print(cr.operators)
    print("number of criterias ", len(cr.criteria))