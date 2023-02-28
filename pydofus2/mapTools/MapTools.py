import math
from functools import lru_cache
from pydofus2.com.ankamagames.jerakine.logger.MemoryProfiler import MemoryProfiler

from pydofus2.com.ankamagames.jerakine.types.positions.MapPoint import MapPoint, Point
from pydofus2.mapTools.MapDirection import MapDirection

MAP_GRID_WIDTH: int = 14
MAP_GRID_HEIGHT: int = 20
MIN_X_COORD: int = 0
MAX_X_COORD: int = 33
MIN_Y_COORD: int = -19
MAX_Y_COORD: int = 13
EVERY_CELL_ID: list
CELLCOUNT: int = 560
INVALID_CELL_ID: int = None
PSEUDO_INFINITE: int = 63
COEFF_FOR_REBASE_ON_CLOSEST_8_DIRECTION: float = math.tan(math.pi / 8)
COORDINATES_DIRECTION: list = ""


def getCellsIdBetween(cell1Id: int, cell2Id: int) -> list:
    precision = 0.0001
    mp1 = MapPoint.fromCellId(cell1Id)
    mp2 = MapPoint.fromCellId(cell2Id)
    if cell1Id == cell2Id or not (isValidCellId(cell1Id) and isValidCellId(cell2Id)):
        return []

    mp1X = mp1.x
    mp1Y = mp1.y
    mp2X = mp2.x
    mp2Y = mp2.y

    xDiff = mp2X - mp1X
    yDiff = mp2Y - mp1Y
    squareDist = math.sqrt(xDiff * xDiff + yDiff * yDiff)

    nxDiff = xDiff / squareDist
    x_step = abs(1 / nxDiff) if nxDiff != 0 else float("inf")
    x_dir = -1 if nxDiff < 0 else 1
    curr_x = 0.5 * x_step

    nyDiff = yDiff / squareDist
    y_step = abs(1 / nyDiff) if nyDiff != 0 else float("inf")
    y_dir = -1 if nyDiff < 0 else 1
    curr_y = 0.5 * y_step

    result = []
    while mp1X != mp2X or mp1Y != mp2Y:

        if abs(curr_x - curr_y) < precision:
            curr_x += x_step
            curr_y += y_step
            mp1X += x_dir
            mp1Y += y_dir

        elif curr_x < curr_y:
            curr_x += x_step
            mp1X += x_dir

        else:
            curr_y += y_step
            mp1Y += y_dir
        result.append(getCellIdByCoord(mp1X, mp1Y))
    return result


def isValidCellId(param1: int) -> bool:
    return 0 <= param1 < CELLCOUNT


def getCellIdByCoord(param1: int, param2: int) -> int:
    if not isValidCoord(param1, param2):
        return -1
    return int(math.floor(float((param1 - param2) * MAP_GRID_WIDTH + param2 + (param1 - param2) / 2)))


def getCellIdXCoord(param1: int) -> int:
    _loc2_: int = math.floor(param1 / MAP_GRID_WIDTH)
    _loc3_: int = math.floor((_loc2_ + 1) / 2)
    _loc4_ = param1 - _loc2_ * MAP_GRID_WIDTH
    return _loc3_ + _loc4_


def getCellIdYCoord(param1: int) -> int:
    _loc2_: int = math.floor(param1 / MAP_GRID_WIDTH)
    _loc3_: int = math.floor((_loc2_ + 1) / 2)
    _loc4_ = _loc2_ - _loc3_
    _loc5_ = param1 - _loc2_ * MAP_GRID_WIDTH
    return _loc5_ - _loc4_


def isValidCoord(param1: int, param2: int) -> bool:
    if param2 >= -param1 and param2 <= param1 and param2 <= MAP_GRID_WIDTH + MAX_Y_COORD - param1:
        return param2 >= param1 - (MAP_GRID_HEIGHT - MIN_Y_COORD)
    return False


def getCellCoordById(cell_id: int) -> Point:
    if not isValidCellId(cell_id):
        return None

    row = math.floor(cell_id / MAP_GRID_WIDTH)
    row_half = math.floor((row + 1) / 2)
    row_offset = row - row_half
    col = cell_id - row * MAP_GRID_WIDTH

    return Point(row_half + col, col - row_offset)


@lru_cache(maxsize=5000)
def getCellsCoordBetween(cellid1: int, cellid2: int) -> list[MapPoint]:
    cellsIds = getCellsIdBetween(cellid1, cellid2)
    return [MapPoint.fromCellId(cellid) for cellid in cellsIds]

@lru_cache(maxsize=5000)
def getDistance(param1: int, param2: int) -> int:
    if not isValidCellId(param1) or not isValidCellId(param2):
        return -1

    x1 = param1 % MAP_GRID_WIDTH
    y1 = (param1 // MAP_GRID_WIDTH + 1) // 2 + x1
    y2 = param1 // MAP_GRID_WIDTH - x1

    x2 = param2 % MAP_GRID_WIDTH
    y3 = (param2 // MAP_GRID_WIDTH + 1) // 2 + x2
    y4 = param2 // MAP_GRID_WIDTH - x2

    return math.floor(abs(y3 - y1) + abs(y4 - y2))


def getLookDirection8Exact(param1: int, param2: int) -> int:
    _loc3_: int = math.floor(param1 / MAP_GRID_WIDTH)
    _loc4_: int = math.floor((_loc3_ + 1) / 2)
    _loc5_ = param1 - _loc3_ * MAP_GRID_WIDTH
    _loc6_: int = math.floor(param1 / MAP_GRID_WIDTH)
    _loc7_: int = math.floor((_loc6_ + 1) / 2)
    _loc8_ = _loc6_ - _loc7_
    _loc9_ = param1 - _loc6_ * MAP_GRID_WIDTH
    _loc10_: int = math.floor(param2 / MAP_GRID_WIDTH)
    _loc11_: int = math.floor((_loc10_ + 1) / 2)
    _loc12_ = param2 - _loc10_ * MAP_GRID_WIDTH
    _loc13_: int = math.floor(param2 / MAP_GRID_WIDTH)
    _loc14_: int = math.floor((_loc13_ + 1) / 2)
    _loc15_ = _loc13_ - _loc14_
    _loc16_ = param2 - _loc13_ * MAP_GRID_WIDTH
    return int(getLookDirection8ExactByCoord(_loc4_ + _loc5_, _loc9_ - _loc8_, _loc11_ + _loc12_, _loc16_ - _loc15_))


def getLookDirection8ExactByCoord(param1: int, param2: int, param3: int, param4: int) -> int:
    _loc5_: int = getLookDirection4ExactByCoord(param1, param2, param3, param4)
    if not MapDirection.isValidDirection(_loc5_):
        _loc5_ = getLookDirection4DiagExactByCoord(param1, param2, param3, param4)
    return _loc5_


def getLookDirection4ExactByCoord(param1: int, param2: int, param3: int, param4: int) -> int:
    if not isValidCoord(param1, param2) or not isValidCoord(param3, param4):
        return -1
    _loc5_ = param3 - param1
    _loc6_ = param4 - param2
    if _loc6_ == 0:
        if _loc5_ < 0:
            return 5
        return 1
    if _loc5_ == 0:
        if _loc6_ < 0:
            return 3
        return 7
    return -1


def getLookDirection4DiagExactByCoord(param1: int, param2: int, param3: int, param4: int) -> int:
    if not isValidCoord(param1, param2) or not isValidCoord(param3, param4):
        return -1
    _loc5_ = param3 - param1
    _loc6_ = param4 - param2
    if _loc5_ == -_loc6_:
        if _loc5_ < 0:
            return 6
        return 2
    if _loc5_ == _loc6_:
        if _loc5_ < 0:
            return 4
        return 0
    return -1
