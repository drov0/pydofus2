import sys

from pydofus2.com.ankamagames.dofus.datacenter.world.MapPosition import \
    MapPosition
from pydofus2.com.ankamagames.jerakine.data.GameData import GameData
from pydofus2.com.ankamagames.jerakine.interfaces.IDataCenter import \
    IDataCenter


class MapCoordinates(IDataCenter):

    MODULE: str = "MapCoordinates"

    UNDEFINED_COORD: int = -sys.maxsize - 1

    compressedCoords: int

    mapIds: list[float]

    _x: int = -2147483648

    _y: int = -2147483648

    _maps: list[MapPosition]

    def __init__(self):
        super().__init__()

    @classmethod
    def getMapCoordinatesByCompressedCoords(cls, compressedCoords: int) -> "MapCoordinates":
        return GameData().getObject(cls.MODULE, compressedCoords)

    @classmethod
    def getMapCoordinatesByCoords(cls, x, y):
        xCompressed = cls.getCompressedValue(x)
        yCompressed = cls.getCompressedValue(y)
        return cls.getMapCoordinatesByCompressedCoords((xCompressed << 16) + yCompressed)

    @classmethod
    def getSignedValue(v):
        isNegative = (v & 32768) > 0
        trueValue = v & 32767
        return -trueValue if isNegative else trueValue

    @classmethod
    def getCompressedValue(cls, v):
        return 32768 | (v & 32767) if v < 0 else v & 32767

    @property
    def x(self) -> int:
        if self._x == self.UNDEFINED_COORD:
            self._x = self.getSignedValue((self.compressedCoords & 4294901760) >> 16)
        return self._x

    @property
    def y(self) -> int:
        if self._y == self.UNDEFINED_COORD:
            self._y = self.getSignedValue(self.compressedCoords & 65535)
        return self._y

    @property
    def maps(self) -> list[MapPosition]:
        i: int = 0
        if not self._maps:
            self._maps = len(list[MapPosition](self.mapIds), True)
            for i in range(len(self.mapIds)):
                self._maps[i] = MapPosition.getMapPositionById(self.mapIds[i])
        return self._maps
