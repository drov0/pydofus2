from com.ankamagames.atouin.data.map.Cell import Cell
from com.ankamagames.atouin.enums.ElementTypesEnum import ElementTypesEnum
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray

logger = Logger(__name__)


class BasicElement:

    _cell: Cell

    def __init__(self, cell: Cell):
        super().__init__()
        self._cell = cell

    @classmethod
    def getElementFromType(cls, type: int, cell: Cell) -> "BasicElement":
        from com.ankamagames.atouin.data.map.elements.GraphicalElement import (
            GraphicalElement,
        )
        from com.ankamagames.atouin.data.map.elements.SoundElement import SoundElement

        if type == ElementTypesEnum.GRAPHICAL:
            return GraphicalElement(cell)
        if type == ElementTypesEnum.SOUND:
            return SoundElement(cell)
        else:
            raise Exception(
                "Un �l�ment de type inconnu "
                + str(type)
                + " a �t� trouv� sur la cellule "
                + str(cell.cellId)
                + "!"
            )

    @property
    def cell(self) -> Cell:
        return self._cell

    @property
    def elementType(self) -> int:
        return -1

    def fromRaw(self, raw: ByteArray, mapVersion: int) -> None:
        raise NotImplementedError
