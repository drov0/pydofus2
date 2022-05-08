from com.ankamagames.dofus.datacenter.idols.Idol import Idol
from com.ankamagames.dofus.datacenter.monsters.Monster import Monster
from com.ankamagames.dofus.datacenter.quest.QuestObjective import QuestObjective
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from com.ankamagames.jerakine.utils.pattern.PatternDecoder import PatternDecoder


class QuestObjectiveFightMonster(QuestObjective, IDataCenter):

    _monster: Monster = None

    _text: str = None

    def __init__(self):
        super().__init__()

    @property
    def monsterId(self) -> int:
        if not self.parameters:
            return 0
        return self.parameters[0]

    @property
    def monster(self) -> Monster:
        if not self._monster:
            self._monster = Monster.getMonsterById(self.monsterId)
        return self._monster

    @property
    def quantity(self) -> int:
        if not self.parameters:
            return 0
        return self.parameters[1]

    @property
    def idolsScore(self) -> int:
        if self.parameters and len(self.parameters) > 2:
            return self.parameters[2]
        return 0

    @property
    def dungeonOnly(self) -> bool:
        if not self.parameters:
            return False
        return self.parameters.dungeonOnly

    @property
    def idolId(self) -> int:
        if self.parameters and len(self.parameters) > 4:
            return self.parameters[4]
        return 0

    @property
    def text(self) -> str:
        monsterLink = None
        idol: Idol = None
        if not self._text:
            if self.idolsScore == 0 and self.idolId == 0:
                self._text = PatternDecoder.getDescription(self.type.name, [monsterLink, self.quantity])
            elif self.idolsScore > 0 and self.idolId == 0:
                self._text = I18n.getUiText(
                    "ui.grimoire.quest.objectives.type6.score", [self.quantity, monsterLink, self.idolsScore]
                )
            elif self.idolsScore > 0 and self.idolId > 0:
                idol = Idol.getIdolById(self.idolId)
                self._text = I18n.getUiText(
                    "ui.grimoire.quest.objectives.type6.scoreAndIdol",
                    [self.quantity, monsterLink, "{item," + str(idol.itemId) + "}", self.idolsScore],
                )
        return self._text
