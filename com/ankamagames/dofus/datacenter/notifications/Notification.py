from com.ankamagames.dofus.types.IdAccessors import IdAccessors
from com.ankamagames.jerakine.data.GameData import GameData
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)


class Notification(IDataCenter):

    MODULE: str = "Notifications"

    id: int

    titleId: int

    messageId: int

    iconId: int

    typeId: int

    trigger: str

    _title: str = None

    _message: str = None

    def __init__(self):
        super().__init__()

    @classmethod
    def getNotificationById(cls, id: int) -> "Notification":
        return GameData.getObject(cls.MODULE, id)

    @classmethod
    def getNotifications(cls) -> list["Notification"]:
        return GameData.getObjects(cls.MODULE)

    idAccessors: IdAccessors = IdAccessors(getNotificationById, getNotifications)

    @property
    def title(self) -> str:
        if not self._title:
            self._title = I18n.getText(self.titleId)
        return self._title

    @property
    def message(self) -> str:
        if not self._message:
            self._message = I18n.getText(self.messageId)
        return self._message
