from com.ankamagames.dofus.types.IdAccessors import IdAccessors
from com.ankamagames.jerakine.data.GameData import GameData
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.interfaces.IDataCenter import IDataCenter
from com.ankamagames.jerakine.logger.Log import Log
from com.ankamagames.jerakine.logger.Logger import Logger
from flash.utils.getQualifiedClassName import getQualifiedClassName

class Characteristic(IDataCenter):

    MODULE:str = "Characteristics"

    logger = Logger(__name__)

    idAccessors:IdAccessors = IdAccessors(getCharacteristicById, getCharacteristics)

    id:int

    keyword:str

    nameId:int

    asset:str

    categoryId:int

    visible:bool

    order:int

    scaleFormulaId:int

    upgradable:bool

    _name:str

    def __init__(self):
        super().__init__()

    @classmethod        def getCharacteristicById(cls, id:int) -> 'Characteristic':        	return GameData.getObject(cls.MODULE, id)

    @classmethod        def getCharacteristics(cls) -> list['Characteristic']:        	return GameData.getObjects(cls.MODULE)

    @property
    def name(self) -> String:
        if not self._name:
            self._name = I18n.getText(self.nameId)
        return self._name


