from com.ankamagames.dofus.types.IdAccessors import IdAccessors
from com.ankamagames.jerakine.data.GameData import GameData
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)


class TaxCollectorFirstname(IDataCenter):

    MODULE: str = "TaxCollectorFirstnames"

    id: int

    firstnameId: int

    _firstname: str

    def __init__(self):
        super().__init__()

    @classmethod
    def getTaxCollectorFirstnameById(cls, id: int) -> "TaxCollectorFirstname":
        return GameData.getObject(cls.MODULE, id)

    idAccessors: IdAccessors = IdAccessors(getTaxCollectorFirstnameById, None)

    @property
    def firstname(self) -> str:
        if not self._firstname:
            self._firstname = I18n.getText(self.firstnameId)
        return self._firstname
