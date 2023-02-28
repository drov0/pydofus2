from typing import Iterator

from pydofus2.com.ankamagames.jerakine.types.enums.DirectionsEnum import \
    DirectionsEnum
from pydofus2.com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from pydofus2.com.ankamagames.jerakine.types.positions.PathElement import \
    PathElement


class MovementPath:

    MAX_PATH_LENGTH: int = 100.0
    
    WALK_HORIZONTAL_DIAG_VELOCITY = 510.0
    WALK_VERTICAL_DIAG_VELOCITY = 425.0
    WALK_LINEAR_VELOCITY = 480.0
    
    RUN_HORIZONTAL_DIAG_VELOCITY = 255
    RUN_VERTICAL_DIAG_VELOCITY = 150
    RUN_LINEAR_VELOCITY = 170

    def __init__(self):
        super().__init__()
        self._oEnd = MapPoint()
        self._oStart = MapPoint()
        self._aPath = list[PathElement]()

    def __getitem__(self, index: int) -> PathElement:
        return self._aPath[index]

    def __iter__(self) -> Iterator[PathElement]:
        return self._aPath.__iter__()

    @property
    def start(self) -> MapPoint:
        return self._oStart

    @start.setter
    def start(self, nValue: MapPoint) -> None:
        self._oStart = nValue

    @property
    def end(self) -> MapPoint:
        return self._oEnd

    @end.setter
    def end(self, nValue: MapPoint) -> None:
        self._oEnd = nValue

    @property
    def path(self) -> list[PathElement]:
        return self._aPath

    @path.setter
    def path(self, value: list[PathElement]) -> None:
        self._aPath = value

    @property
    def length(self) -> int:
        return len(self._aPath)

    def indexOfCell(self, cellId: int) -> int:
        for i, pe in enumerate(self.path):
            if int(pe.cellId) == int(cellId):
                return i
        return None

    def fillFromCellIds(self, cells: list[int]) -> None:
        for cell in cells:
            self._aPath.append(PathElement(MapPoint.fromCellId(cell)))
        for i in range(len(cells) - 1):
            self._aPath[i].orientation = self._aPath[i].step.orientationTo(self._aPath[i + 1].step)
        if len(self._aPath) > 0:
            self._oStart = self._aPath[0].step
            self._oEnd = self._aPath[-1].step

    def addPoint(self, pathElem: PathElement) -> None:
        self._aPath.append(pathElem)

    def getPointAtIndex(self, index: int) -> PathElement:
        return self._aPath[index]

    def deletePoint(self, index: int, deleteCount: int = 1) -> None:
        if deleteCount == 0:
            del self._aPath[index:]
        else:
            del self._aPath[index : index + deleteCount]

    def __str__(self) -> str:
        res = f"start | "
        res += " | ".join([str(p.step.cellId) for p in self._aPath])
        res += f" | {self._oEnd.cellId} | end"
        return res

    def compress(self) -> None:
        elem: int = 0
        if len(self._aPath) > 0:
            elem = len(self._aPath) - 1
            while elem > 0:
                if self._aPath[elem].orientation == self._aPath[elem - 1].orientation:
                    self.deletePoint(elem)
                elem -= 1

    def fill(self) -> None:
        if len(self._aPath) > 0:
            elem = 0
            pFinal = PathElement()
            pFinal.orientation = DirectionsEnum.RIGHT
            pFinal.step = self._oEnd
            self._aPath.append(pFinal)
            while elem < len(self._aPath) - 1:
                # Logger().debug(f"({self._aPath[elem].step}, {self._aPath[elem].orientation}) and ({self._aPath[elem + 1].step}, {self._aPath[elem + 1].orientation})")
                if (
                    abs(self._aPath[elem].step.x - self._aPath[elem + 1].step.x) > 1
                    or abs(self._aPath[elem].step.y - self._aPath[elem + 1].step.y) > 1
                ):
                    pe = PathElement()
                    pe.orientation = DirectionsEnum(self._aPath[elem].orientation)
                    if pe.orientation == DirectionsEnum.RIGHT:
                        pe.step = MapPoint.fromCoords(self._aPath[elem].step.x + 1, self._aPath[elem].step.y + 1)

                    elif pe.orientation == DirectionsEnum.DOWN_RIGHT:
                        pe.step = MapPoint.fromCoords(self._aPath[elem].step.x + 1, self._aPath[elem].step.y)

                    elif pe.orientation == DirectionsEnum.DOWN:
                        pe.step = MapPoint.fromCoords(self._aPath[elem].step.x + 1, self._aPath[elem].step.y - 1)

                    elif pe.orientation == DirectionsEnum.DOWN_LEFT:
                        pe.step = MapPoint.fromCoords(self._aPath[elem].step.x, self._aPath[elem].step.y - 1)

                    elif pe.orientation == DirectionsEnum.LEFT:
                        pe.step = MapPoint.fromCoords(self._aPath[elem].step.x - 1, self._aPath[elem].step.y - 1)

                    elif pe.orientation == DirectionsEnum.UP_LEFT:
                        pe.step = MapPoint.fromCoords(self._aPath[elem].step.x - 1, self._aPath[elem].step.y)

                    elif pe.orientation == DirectionsEnum.UP:
                        pe.step = MapPoint.fromCoords(self._aPath[elem].step.x - 1, self._aPath[elem].step.y + 1)

                    elif pe.orientation == DirectionsEnum.UP_RIGHT:
                        pe.step = MapPoint.fromCoords(self._aPath[elem].step.x, self._aPath[elem].step.y + 1)

                    else:
                        raise ValueError("Invalid orientation :" + str(pe.orientation))

                    self._aPath.insert(elem + 1, pe)
                    elem += 1
                else:
                    elem += 1
                if elem > self.MAX_PATH_LENGTH:
                    raise Exception("Path too long. Maybe an orientation problem?")
            self._aPath.pop()

    def __len__(self) -> int:
        return len(self._aPath)

    def getCells(self) -> list[int]:
        mp: MapPoint = None
        cells: list[int] = list[int]()
        for i in range(len(self._aPath)):
            mp = self._aPath[i].step
            cells.append(mp.cellId)
        cells.append(self._oEnd.cellId)
        return cells

    def replaceEnd(self, newEnd: MapPoint) -> None:
        self._oEnd = newEnd

    def clone(self) -> "MovementPath":
        clonePath: MovementPath = MovementPath()
        clonePath.start = self._oStart
        clonePath.end = self._oEnd
        clonePath.path = self._aPath.copy()
        return clonePath

    def getCrossingDuration(self, run: bool = True) -> int:
        duration = 0
        for i in range(1, len(self._aPath)):
            orientation = self._aPath[i - 1].orientation
            if not run:
                if orientation % 2 == 0:
                    if orientation % 4 == 0:
                        duration += self.WALK_HORIZONTAL_DIAG_VELOCITY
                    duration += self.WALK_VERTICAL_DIAG_VELOCITY
                duration += self.WALK_LINEAR_VELOCITY
            else:
                if orientation % 2 == 0:
                    if orientation % 4 == 0:
                        duration += self.RUN_HORIZONTAL_DIAG_VELOCITY
                    duration += self.RUN_VERTICAL_DIAG_VELOCITY
                duration += self.RUN_LINEAR_VELOCITY
        return duration / 1000.0
    
    def keyMoves(self) -> list[int]:
        self.compress()
        movement: list[int] = list[int]()
        for pe in self.path:
            lastOrientation = pe.orientation
            value = (int(lastOrientation) & 7) << 12 | pe.step.cellId & 4095
            movement.append(value)
        lastValue = (int(lastOrientation) & 7) << 12 | self.end.cellId & 4095
        movement.append(lastValue)
        return movement

    @classmethod
    def fromClientMovement(cls, path: list[int]) -> "MovementPath":
        mp: MovementPath = MovementPath()
        moveCount: int = 0
        previousElement = None
        for movement in path:
            destination = MapPoint.fromCellId(movement & 4095)
            pe = PathElement()
            pe.step = destination
            if moveCount == 0:
                mp.start = destination
            else:
                previousElement.orientation = previousElement.step.orientationTo(pe.step)
            if moveCount == len(path) - 1:
                mp.end = destination
                break
            mp.addPoint(pe)
            previousElement = pe
            moveCount += 1
        mp.fill()
        return mp
