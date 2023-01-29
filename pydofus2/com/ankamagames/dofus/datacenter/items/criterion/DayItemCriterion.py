from pydofus2.com.ankamagames.dofus.datacenter.items.criterion import ItemCriterion
from pydofus2.com.ankamagames.jerakine.interfaces import IDataCenter
from pydofus2.com.ankamagames.jerakine.utils.pattern import PatternDecoder
from pydofus2.com.ankamagames.jerakine.data import I18n
from pydofus2.com.ankamagames.dofus.datacenter.items.criterion import IItemCriterion


class DayItemCriterion(ItemCriterion, IDataCenter):
    def __init__(self, pCriterion: str):
        super().__init__(pCriterion)

    @property
    def text(self) -> str:
        readableCriterionValue: str = str(self._criterionValue)
        readableCriterionRef: str = PatternDecoder.combine(I18n.getUiText("ui.time.days"), "n", True)
        return readableCriterionRef + " " + self._operator.text + " " + readableCriterionValue

    def clone(self) -> "IItemCriterion":
        return DayItemCriterion(self.basicText)

    def getCriterion(self) -> int:
        date: Date = Date()
        return TimeManager().getDateFromTime(date.getTime())[2]
