from com.ankamagames.dofus.datacenter.quest.QuestObjective import QuestObjective
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from com.ankamagames.jerakine.utils.pattern.PatternDecoder import PatternDecoder


class QuestObjectiveDiscoverMap(QuestObjective, IDataCenter):

    _mapDescriptionText: str = ""

    _text: str = ""

    def __init__(self):
        super().__init__()

    @property
    def mapDescriptionTextId(self) -> int:
        if not self.parameters:
            return 0
        return self.parameters[0]

    @property
    def mapDescriptionText(self) -> str:
        if not self._mapDescriptionText:
            self._mapDescriptionText = I18n.getText(self.mapDescriptionTextId)
        return self._mapDescriptionText

    @property
    def text(self) -> str:
        if not self._text:
            self._text = PatternDecoder.getDescription(self.type.name, [self.mapDescriptionText])
        return self._text
