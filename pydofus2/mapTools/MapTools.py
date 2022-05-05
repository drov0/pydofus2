import math
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint, Point
from mapTools.MapDirection import MapDirection

MAP_GRID_WIDTH: int = 14
MAP_GRID_HEIGHT: int = 20
MIN_X_COORD: int = 0
MAX_X_COORD: int = 33
MIN_Y_COORD: int = -19
MAX_Y_COORD: int = 13
EVERY_CELL_ID: list
mapCountCell: int = 560
INVALID_CELL_ID: int = -1
PSEUDO_INFINITE: int = 63
COEFF_FOR_REBASE_ON_CLOSEST_8_DIRECTION: float = math.tan(math.pi / 8)
COORDINATES_DIRECTION: list = ""

logger = Logger("pyd2bot")


def getCellsIdBetween(param1: int, param2: int) -> list:
    mp1 = MapPoint.fromCellId(param1)
    mp2 = MapPoint.fromCellId(param2)
    # logger.debug(f"getCellsIdBetween({mp1}, {mp2})")
    if param1 == param2:
        return []
    if not isValidCellId(param1) or not isValidCellId(param2):
        return []
    mp1X = mp1.x
    mp1Y = mp1.y
    mp2X = mp2.x
    mp2Y = mp2.y
    xDiff = mp2X - mp1X
    yDiff = mp2Y - mp1Y
    squareDist: float = float(math.sqrt(xDiff * xDiff + yDiff * yDiff))
    nxDiff: float = xDiff / squareDist
    nyDiff: float = yDiff / squareDist
    xnStep: float = float(abs(1 / nxDiff)) if nxDiff != 0 else float("inf")
    ynStep: float = float(abs(1 / nyDiff)) if nyDiff != 0 else float("inf")
    dx: int = -1 if nxDiff < 0 else 1
    dy: int = -1 if nyDiff < 0 else 1
    halfXSTep: float = 0.5 * xnStep
    halfYStep: float = 0.5 * ynStep
    result: list = []
    while mp1X != mp2X or mp1Y != mp2Y:
        if floatAlmostEquals(halfXSTep, halfYStep):
            halfXSTep += xnStep
            halfYStep += ynStep
            mp1X += dx
            mp1Y += dy

        elif halfXSTep < halfYStep:
            halfXSTep += xnStep
            mp1X += dx

        else:
            halfYStep += ynStep
            mp1Y += dy
        result.append(int(getCellIdByCoord(mp1X, mp1Y)))
    return result


def isValidCellId(param1: int) -> bool:
    # if not isInit:
    #     raise  Exception("MapTools must be initiliazed with method .initForDofus2 or .initForDofus3")
    if param1 >= 0:
        return param1 < mapCountCell
    return False


def floatAlmostEquals(param1: float, param2: float) -> bool:
    if param1 != param2:
        if param1 == float("inf") or param2 == float("inf"):
            return False
        return float(abs(param1 - param2)) < 0.0001
    return True


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


def getCellCoordById(param1: int) -> Point:
    if not isValidCellId(param1):
        return None
    _loc2_: int = math.floor(param1 / MAP_GRID_WIDTH)
    _loc3_: int = math.floor((_loc2_ + 1) / 2)
    _loc4_ = _loc2_ - _loc3_
    _loc5_ = param1 - _loc2_ * MAP_GRID_WIDTH
    return Point(_loc3_ + _loc5_, _loc5_ - _loc4_)


def getCellsCoordBetween(param1: int, param2: int) -> list[MapPoint]:
    cellsIds = getCellsIdBetween(param1, param2)
    return [MapPoint.fromCellId(cellid) for cellid in cellsIds]


def getDistance(param1: int, param2: int) -> int:
    if not isValidCellId(param1) or not isValidCellId(param2):
        return -1
    _loc3_: int = math.floor(param1 / MAP_GRID_WIDTH)
    _loc4_: int = math.floor((_loc3_ + 1) / 2)
    _loc5_ = param1 - _loc3_ * MAP_GRID_WIDTH
    _loc6_ = _loc4_ + _loc5_
    _loc7_: int = math.floor(param1 / MAP_GRID_WIDTH)
    _loc8_: int = math.floor((_loc7_ + 1) / 2)
    _loc9_ = _loc7_ - _loc8_
    _loc10_ = param1 - _loc7_ * MAP_GRID_WIDTH
    _loc11_ = _loc10_ - _loc9_
    _loc12_: int = math.floor(param2 / MAP_GRID_WIDTH)
    _loc13_: int = math.floor((_loc12_ + 1) / 2)
    _loc14_ = param2 - _loc12_ * MAP_GRID_WIDTH
    _loc15_ = _loc13_ + _loc14_
    _loc16_: int = math.floor(param2 / MAP_GRID_WIDTH)
    _loc17_: int = math.floor((_loc16_ + 1) / 2)
    _loc18_ = _loc16_ - _loc17_
    _loc19_ = param2 - _loc16_ * MAP_GRID_WIDTH
    _loc20_ = _loc19_ - _loc18_
    return math.floor(abs(_loc15_ - _loc6_) + abs(_loc20_ - _loc11_))


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
