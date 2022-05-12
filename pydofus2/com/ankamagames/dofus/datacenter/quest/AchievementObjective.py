from com.ankamagames.dofus.types.IdAccessors import IdAccessors
from com.ankamagames.jerakine.data.GameData import GameData
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from com.ankamagames.jerakine.logger.Logger import Logger


class AchievementObjective(IDataCenter):

    logger = Logger("pyd2bot")

    MODULE: str = "AchievementObjectives"

    id: int

    achievementId: int

    order: int

    nameId: int

    criterion: str

    _name: str = None

    def __init__(self):
        super().__init__()

    @classmethod
    def getAchievementObjectiveById(cls, id: int) -> "AchievementObjective":
        return GameData.getObject(cls.MODULE, id)

    @classmethod
    def getAchievementObjectives(cls) -> list["AchievementObjective"]:
        return GameData.getObjects(cls.MODULE)

    @property
    def name(self) -> str:
        if not self._name:
            self._name = I18n.getText(self.nameId)
        return self._name

    idAccessors: IdAccessors = IdAccessors(getAchievementObjectiveById, getAchievementObjectives)
