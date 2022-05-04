import math
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.map.IDataMapProvider import IDataMapProvider
from com.ankamagames.jerakine.map.ILosDetector import ILosDetector
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from mapTools import MapTools

logger = Logger(__name__)


class LosDetector(ILosDetector):
    @classmethod
    def losBetween(
        cls, mapProvider: IDataMapProvider, refPos: MapPoint, targetPos: MapPoint, tested: dict[str, bool] = {}
    ) -> bool:
        los = True
        if f"{targetPos.x}_{targetPos.y}" not in tested or refPos.inDiag(targetPos):
            line = MapTools.getCellsCoordBetween(refPos.cellId, targetPos.cellId)
            if len(line) == 0:
                return True
            else:
                for j in range(len(line)):
                    ptKey = f"{math.floor(line[j].x)}_{math.floor(line[j].y)}"
                    if MapPoint.isInMap(line[j].x, line[j].y):
                        if j > 0 and mapProvider.hasEntity(math.floor(line[j - 1].x), math.floor(line[j - 1].y), True):
                            los = False
                        elif ptKey not in tested or refPos.inDiag(line[j]):
                            los = los and mapProvider.pointLos(math.floor(line[j].x), math.floor(line[j].y), True)
                        else:
                            los = los and tested[ptKey]
                        if not los:
                            break
        tested[ptKey] = los
        return los

    @classmethod
    def getCell(cls, mapProvider: IDataMapProvider, spellrange: list[int], refPosition: MapPoint) -> list[int]:
        orderedCell: list = list()
        for cellId in spellrange:
            mp = MapPoint.fromCellId(cellId)
            orderedCell.append({"p": mp, "dist": refPosition.distanceToCell(mp)})
        sorted(orderedCell, key=lambda x: x["dist"], reverse=True)
        tested = dict[str, bool]()
        result: list[int] = list[int]()
        for i in range(len(orderedCell)):
            p: MapPoint = orderedCell[i]["p"]

            if (
                tested.get(f"{p.x}_{p.y}") is None
                or refPosition.x + refPosition.y == p.x + p.y
                or refPosition.x - refPosition.y == p.x - p.y
            ):
                line = MapTools.getCellsCoordBetween(refPosition.cellId, p.cellId)
                if len(line) == 0:
                    result.append(p.cellId)

                else:
                    los = True
                    for j in range(len(line)):
                        currentPoint = f"{math.floor(line[j].x)}_{math.floor(line[j].y)}"
                        if MapPoint.isInMap(line[j].x, line[j].y):
                            if j > 0 and mapProvider.hasEntity(
                                math.floor(line[j - 1].x), math.floor(line[j - 1].y), True
                            ):
                                los = False

                            elif (
                                line[j].x + line[j].y == refPosition.x + refPosition.y
                                or line[j].x - line[j].y == refPosition.x - refPosition.y
                            ):
                                los = los and mapProvider.pointLos(math.floor(line[j].x), math.floor(line[j].y))

                            elif tested.get(currentPoint) is None:
                                los = los and mapProvider.pointLos(math.floor(line[j].x), math.floor(line[j].y))

                            else:
                                los = los and tested[currentPoint]
                    tested[currentPoint] = los

        for i in spellrange:
            mp = MapPoint.fromCellId(i)
            if tested[f"{mp.x}_{mp.y}"]:
                result.append(mp.cellId)

        return result
