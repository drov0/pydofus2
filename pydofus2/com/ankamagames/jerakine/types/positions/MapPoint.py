import math
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.map.IDataMapProvider import IDataMapProvider
from com.ankamagames.jerakine.map.ILosDetector import ILosDetector
from com.ankamagames.jerakine.types.enums.DirectionsEnum import DirectionsEnum
from flash.geom.Point import Point

logger = Logger("Dofus2")


class MapPoint:
    RIGHT = 0
    DOWN_RIGHT = 1
    DOWN = 2
    DOWN_LEFT = 3
    LEFT = 4
    UP_LEFT = 5
    UP = 6
    UP_RIGHT = 7
    MAP_WIDTH = 14
    MAP_HEIGHT = 20
    CELLPOS = dict[int, Point]()
    VECTOR_RIGHT = Point(1, 1)
    VECTOR_DOWN_RIGHT = Point(1, 0)
    VECTOR_DOWN = Point(1, -1)
    VECTOR_DOWN_LEFT = Point(0, -1)
    VECTOR_LEFT = Point(-1, -1)
    VECTOR_UP_LEFT = Point(-1, 0)
    VECTOR_UP = Point(-1, 1)
    VECTOR_UP_RIGHT = Point(0, 1)
    _bInit = False

    def __init__(self, cellId=None, x=None, y=None) -> None:
        self._bInit = True
        self._nCellId = cellId
        self._nX = x
        self._nY = y

    def setFromCellId(self):
        if not MapPoint._bInit:
            MapPoint.init()
        p = self.CELLPOS[self._nCellId]
        self._nX = p.x
        self._nY = p.y

    def setFromCoords(self):
        if not MapPoint._bInit:
            MapPoint.init()
        self._nCellId = (self._nX - self._nY) * MapPoint.MAP_WIDTH + self._nY + (self._nX - self._nY) // 2

    @classmethod
    def fromCellId(cls, cellId: int):
        mp = cls(cellId)
        mp.setFromCellId()
        return mp

    @classmethod
    def fromCoords(cls, x: int, y: int):
        mp = cls()
        mp._nX = x
        mp._nY = y
        mp.setFromCoords()
        return mp

    @staticmethod
    def getOrientationsDistance(currentOrientation: int, defaultOrientation: int) -> int:
        return min(abs(defaultOrientation - currentOrientation), abs(8 - defaultOrientation + currentOrientation))

    @staticmethod
    def isInMap(i1: int, i2: int):
        return i1 + i2 >= 0 and i1 - i2 >= 0 and i1 - i2 < MapPoint.MAP_HEIGHT * 2 and i1 + i2 < MapPoint.MAP_WIDTH * 2

    @classmethod
    def init(cls):
        cls._bInit = True
        i1 = 0
        i2 = 0
        i3 = 0
        for _ in range(cls.MAP_HEIGHT):
            for j in range(cls.MAP_WIDTH):
                cls.CELLPOS[i3] = Point(i1 + j, i2 + j)
                i3 += 1
            i1 += 1
            for j in range(cls.MAP_WIDTH):
                cls.CELLPOS[i3] = Point(i1 + j, i2 + j)
                i3 += 1
            i2 -= 1

    @property
    def cellId(self) -> int:
        return self._nCellId

    @cellId.setter
    def cellId(self, i: int):
        if not type(i) == int:
            raise TypeError("cellId must be an int")
        self._nCellId = i
        self.setFromCellId()

    @property
    def x(self) -> int:
        return self._nX

    @x.setter
    def x(self, i: int):
        self._nX = i
        self.setFromCoords()

    @property
    def y(self) -> int:
        return self._nY

    @y.setter
    def y(self, i: int):
        self._nY = i
        self.setFromCoords()

    def getCoordinates(self) -> Point:
        return Point(self._nX, self._nY)

    def distanceTo(self, mp: "MapPoint") -> int:
        return math.sqrt((self.x - mp.x) ** 2 + (self.y - mp.y) ** 2)

    def distanceToCell(self, mp: "MapPoint"):
        return abs(self.x - mp.x) + abs(self.y - mp.y)

    def orientationTo(self, mp: "MapPoint") -> int:
        if self._nX == mp._nX and self._nY == mp._nY:
            return DirectionsEnum.DOWN_RIGHT.value
        p = Point()
        p.x = 1 if mp._nX > self._nX else (-1 if mp._nX < self._nX else 0)
        p.y = 1 if mp._nY > self._nY else (-1 if mp._nY < self._nY else 0)
        nb = DirectionsEnum.RIGHT
        if p.x == self.VECTOR_RIGHT.x and p.y == self.VECTOR_RIGHT.y:
            nb = DirectionsEnum.RIGHT

        elif p.x == self.VECTOR_DOWN_RIGHT.x and p.y == self.VECTOR_DOWN_RIGHT.y:
            nb = DirectionsEnum.DOWN_RIGHT

        elif p.x == self.VECTOR_DOWN.x and p.y == self.VECTOR_DOWN.y:
            nb = DirectionsEnum.DOWN

        elif p.x == self.VECTOR_DOWN_LEFT.x and p.y == self.VECTOR_DOWN_LEFT.y:
            nb = DirectionsEnum.DOWN_LEFT

        elif p.x == self.VECTOR_LEFT.x and p.y == self.VECTOR_LEFT.y:
            nb = DirectionsEnum.LEFT

        elif p.x == self.VECTOR_UP_LEFT.x and p.y == self.VECTOR_UP_LEFT.y:
            nb = DirectionsEnum.UP_LEFT

        elif p.x == self.VECTOR_UP.x and p.y == self.VECTOR_UP.y:
            nb = DirectionsEnum.UP

        elif p.x == self.VECTOR_UP_RIGHT.x and p.y == self.VECTOR_UP_RIGHT.y:
            nb = DirectionsEnum.UP_RIGHT
        return nb.value

    def advancedOrientationTo(self, target: "MapPoint", fourDir: bool = True) -> int:
        if target is None:
            return 0
        xdiff = target.x - self.x
        ydiff = target.y - self.y
        dist = math.sqrt(xdiff**2 + ydiff**2)
        angle = math.acos(xdiff / dist) * 180 / math.pi * (1 if ydiff > 0 else -1)
        if fourDir:
            angle = round(angle / 90) * 2 + 1
        else:
            angle = round(angle / 45) + 1
        if angle < 0:
            angle += 8
        return angle

    def advancedOrientationTo2(self, target: "MapPoint", fourDir: bool = True) -> int:
        if target is None:
            return 0
        target_theta = math.atan2(target.x, target.y)
        self_theta = math.atan2(self.x, self.y)
        angle = self_theta - target_theta
        logger.debug("angle: %f", angle / math.pi * 180)
        if fourDir:
            angle = round(2 * (angle / math.pi)) + 1 % 8
        else:
            angle = round(4 * (angle / math.pi)) + 1 % 8
        return angle

    def pointSymetry(self, mp: "MapPoint") -> "MapPoint":
        i1 = 2 * mp.x - self.x
        i2 = 2 * mp.y - self.y
        if self.isInMap(i1, i2):
            return MapPoint.fromCoords(i1, i2)
        return None

    def los(self, losDetector: ILosDetector, provider: IDataMapProvider, target: "MapPoint", tested: dict[int, bool]):
        return losDetector.losBetween(provider, self, target, tested)

    def getNearestFreeCell(self, mapProvider: IDataMapProvider, allowThoughEntity: bool = True) -> "MapPoint":
        for i in range(8):
            mp = self.getNearestFreeCellInDirection(i, mapProvider, False, allowThoughEntity)
            if mp:
                return mp

    def vicinity(self, fourDir) -> list["MapPoint"]:
        res = []
        for i in range(8):
            if i % 2 == 1:
                mp = self.getNearestCellInDirection(i)
                if mp is not None:
                    res.append(mp)
        return res

    def getNearestCellInDirection(self, orientation: int) -> "MapPoint":
        if orientation == 0:
            mp = MapPoint.fromCoords(self._nX + 1, self._nY + 1)
        elif orientation == 1:
            mp = MapPoint.fromCoords(self._nX + 1, self._nY)
        elif orientation == 2:
            mp = MapPoint.fromCoords(self._nX + 1, self._nY - 1)
        elif orientation == 3:
            mp = MapPoint.fromCoords(self._nX, self._nY - 1)
        elif orientation == 4:
            mp = MapPoint.fromCoords(self._nX - 1, self._nY - 1)
        elif orientation == 5:
            mp = MapPoint.fromCoords(self._nX - 1, self._nY)
        elif orientation == 6:
            mp = MapPoint.fromCoords(self._nX - 1, self._nY + 1)
        elif orientation == 7:
            mp = MapPoint.fromCoords(self._nX, self._nY + 1)
        if MapPoint.isInMap(mp._nX, mp._nY):
            return mp
        return None

    def inDiag(self, mp: "MapPoint") -> bool:
        return abs(self.x - mp.x) == abs(self.y - mp.y)

    def pointMov(self, provider: IDataMapProvider, dest: "MapPoint", allowThoughEntity: bool) -> bool:
        return provider.pointMov(dest.x, dest.y, allowThoughEntity, self.cellId)

    def getNearestFreeCellInDirection(
        self,
        orientation: int,
        mapProvider: IDataMapProvider,
        allowItself: bool = True,
        allowThoughEntity: bool = True,
        ignoreSpeed: bool = False,
        forbidenCellsId: list = None,
    ) -> "MapPoint":
        if forbidenCellsId is None:
            forbidenCellsId = list()
        cells: list[MapPoint] = list[MapPoint](8 * [None])
        weights: list[int] = list[int](8 * [-1])
        orientationDist = [MapPoint.getOrientationsDistance(i, orientation) for i in range(8)]
        for i in range(8):
            mp = self.getNearestCellInDirection(i)
            cells[i] = mp
            if mp is not None:
                speed = mapProvider.getCellSpeed(mp.cellId)
                if mp.cellId not in forbidenCellsId:
                    if mapProvider.pointMov(mp._nX, mp._nY, allowThoughEntity, self.cellId):
                        weights[i] = orientationDist[i] + (
                            (5 - speed if speed >= 0 else 11 + abs(speed)) if not ignoreSpeed else 0
                        )
                    else:
                        forbidenCellsId.append(mp.cellId)
                        weights[i] = -1
                else:
                    if mapProvider.pointMov(mp._nX, mp._nY, allowThoughEntity, self.cellId):
                        weights[i] = (
                            100
                            + orientationDist[i]
                            + ((5 - speed if speed >= 0 else 11 + abs(speed)) if not ignoreSpeed else 0)
                        )
                    else:
                        weights[i] = -1
            else:
                weights[i] = -1
        minWeightOrientation: int = -1
        minWeight: int = 10000
        for i in range(8):
            if weights[i] != -1 and weights[i] < minWeight and cells[i] is not None:
                minWeight = weights[i]
                minWeightOrientation = i
        if minWeightOrientation != -1:
            mp = cells[minWeightOrientation]
        else:
            mp = None
        if mp is None and allowItself and mapProvider.pointMov(self._nX, self._nY, allowThoughEntity, self.cellId):
            return self
        return mp

    def __eq__(self, mp: "MapPoint") -> bool:
        if not isinstance(mp, MapPoint):
            raise TypeError("mp must be a MapPoint")
        return self._nCellId == mp._nCellId

    def __str__(self):
        return f"MapPoint(x: {self.x}, y: {self.y}, id: {self.cellId})"

    def __hash__(self) -> int:
        return self._nCellId
