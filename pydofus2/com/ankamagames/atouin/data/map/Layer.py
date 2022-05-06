from com.ankamagames.atouin.AtouinConstants import AtouinConstants
from com.ankamagames.atouin.data.map.elements.BasicElement import BasicElement
from com.ankamagames.atouin.data.map.elements.GraphicalElement import GraphicalElement
from com.ankamagames.atouin.data.map.elements.SoundElement import SoundElement
from com.ankamagames.atouin.enums.ElementTypesEnum import ElementTypesEnum
from com.ankamagames.jerakine.data.BinaryStream import BinaryStream
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger("Dofus2")


class Layer:

    LAYER_GROUND = 0

    LAYER_ADDITIONAL_GROUND = 1

    LAYER_DECOR = 2

    LAYER_ADDITIONAL_DECOR = 3

    def __init__(self, raw, mapVersion):
        self.version = mapVersion
        self.read(raw)

    def read(self, raw: BinaryStream):
        if self.version >= 9:
            self.layerId = raw.readByte()

        else:
            self.layerId = raw.readInt()
        self.cellsCount = raw.readShort()
        self.cells = [LayerCell(raw, self.version) for _ in range(self.cellsCount)]


class LayerCell:
    def __init__(self, raw: BinaryStream, mapVersion):
        self.mapVersion = mapVersion
        self.read(raw)

    def read(self, raw: BinaryStream):
        self.cellId = raw.readShort()
        self.elementsCount = raw.readShort()
        self.elements: list[BasicElement] = [None] * self.elementsCount
        for i in range(self.elementsCount):
            be = BasicElement.getElementFromType(raw.readByte(), self)
            if AtouinConstants.DEBUG_FILES_PARSING:
                logger.debug("    (Cell) Element at index " + i + " :")
            be.fromRaw(raw, self.mapVersion)
            self.elements[i] = be
