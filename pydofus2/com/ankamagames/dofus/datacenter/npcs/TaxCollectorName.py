from com.ankamagames.dofus.types.IdAccessors import IdAccessors
from com.ankamagames.jerakine.data.GameData import GameData
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)


class TaxCollectorName(IDataCenter):
    MODULE: str = "TaxCollectorNames"

    id: int

    nameId: int

    _name: str

    def __init__(self):
        super().__init__()

    @classmethod
    def getTaxCollectorNameById(cls, id: int) -> "TaxCollectorName":
        return GameData.getObject(cls.MODULE, id)

    @classmethod
    def getTaxCollectorNames(cls) -> list["TaxCollectorName"]:
        return GameData.getObjects(cls.MODULE)

    idAccessors: IdAccessors = IdAccessors(
        getTaxCollectorNameById, getTaxCollectorNames
    )

    @property
    def name(self) -> str:
        if not self._name:
            self._name = I18n.getText(self.nameId)
        return self._name
