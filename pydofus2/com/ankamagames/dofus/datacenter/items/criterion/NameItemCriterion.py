from pydofus2.com.ankamagames.dofus.datacenter.items.criterion import ItemCriterion
from pydofus2.com.ankamagames.jerakine.interfaces import IDataCenter
from pydofus2.com.ankamagames.dofus.logic.game.common.managers import PlayedCharacterManager
from pydofus2.com.ankamagames.jerakine.data import I18n
from pydofus2.com.ankamagames.dofus.datacenter.items.criterion import IItemCriterion


class NameItemCriterion(ItemCriterion, IDataCenter):
    def __init__(self, pCriterion: str):
        super().__init__(pCriterion)

    @property
    def text(self) -> str:
        readableCriterionRef: str = I18n.getUiText("ui.common.name")
        return readableCriterionRef + " " + self.getReadableOperator()

    @property
    def isRespected(self) -> bool:
        name: str = PlayedCharacterManager().infos.name
        respected = False
        criterionValue: str = str(self._criterionValue)
        if self._operator.text == "=":
            respected = name == criterionValue

        if self._operator.text == "!":
            respected = name != criterionValue

        if self._operator.text == "~":
            respected = name.toLowerCase() == criterionValue.toLowerCase()

        if self._operator.text == "S":
            respected = name.toLowerCase().index(criterionValue.toLowerCase()) == 0

        if self._operator.text == "s":
            respected = name.index(criterionValue) == 0

        if self._operator.text == "E":
            respected = name.toLowerCase().index(criterionValue.toLowerCase()) == len(name) - len(criterionValue)

        if self._operator.text == "e":
            respected = name.index(criterionValue) == len(name) - len(criterionValue)

        if self._operator.text == "v" or self._operator.text == "i":
            return respected

    def clone(self) -> "IItemCriterion":
        return NameItemCriterion(self.basicText)

    def getCriterion(self) -> int:
        return 0

    def getReadableOperator(self) -> str:
        text: str = ""
        if self._operator.text == "!" or self._operator.text == "=":
            text = self._operator.text + " " + self._criterionValueText

        elif self._operator.text == "~":
            text = "= " + self._criterionValueText

        elif self._operator.text == "S" or self._operator.text == "s":
            text = I18n.getUiText("ui.criterion.startWith", [self._criterionValueText])

        elif self._operator.text == "E" or self._operator.text == "e":
            text = I18n.getUiText("ui.criterion.endWith", [self._criterionValueText])

        elif self._operator.text == "v":
            text = I18n.getUiText("ui.criterion.valid")

        elif self._operator.text == "i":
            text = I18n.getUiText("ui.criterion.invalid")
        return text
