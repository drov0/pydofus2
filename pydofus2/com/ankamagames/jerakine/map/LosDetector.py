import math
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.map.IDataMapProvider import IDataMapProvider
from com.ankamagames.jerakine.map.ILosDetector import ILosDetector
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from mapTools import MapTools

logger = Logger("pyd2bot")


class LosDetector(ILosDetector):
    @classmethod
    def losBetween(
        cls, mapProvider: IDataMapProvider, refPos: MapPoint, targetPos: MapPoint, tested: dict[str, bool] = {}
    ) -> bool:
        los = False
        ptKey = f"{targetPos.x}_{targetPos.y}"
        if ptKey in tested:
            return tested[ptKey]
        line = MapTools.getCellsCoordBetween(refPos.cellId, targetPos.cellId)
        if len(line) == 0:
            los = True
        else:
            for j in range(len(line)):
                ptKey = f"{line[j].x}_{line[j].y}"
                if MapPoint.isInMap(line[j].x, line[j].y):
                    if j > 0 and mapProvider.hasEntity(line[j - 1].x, line[j - 1].y, True):
                        los = False
                    elif ptKey not in tested or refPos.inDiag(line[j]):
                        los = los and mapProvider.pointLos(line[j].x, line[j].y, True)
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
        orderedCell.sort(key=lambda x: x["dist"], reverse=True)
        tested = dict[str, bool]()
        result: list[int] = list[int]()
        for i in range(len(orderedCell)):
            p: MapPoint = orderedCell[i]["p"]
            if p not in tested or abs(p.x - refPosition.x) == abs(p.y - refPosition.y):
                line = MapTools.getCellsCoordBetween(refPosition.cellId, p.cellId)
                if len(line) == 0:
                    result.append(p.cellId)
                else:
                    los = True
                    for j in range(len(line)):
                        if MapPoint.isInMap(line[j].x, line[j].y):
                            if j > 0 and mapProvider.hasEntity(line[j - 1].x, line[j - 1].y, True):
                                los = False

                            elif line[j] not in tested or abs(line[j].x - refPosition.x) == abs(
                                line[j].y - refPosition.y
                            ):
                                los = los and mapProvider.pointLos(line[j].x, line[j].y, True)

                            else:
                                los = los and tested[line[j]]
                    tested[line[j]] = los
        for i in spellrange:
            mp = MapPoint.fromCellId(i)
            if tested[mp]:
                result.append(mp)

        return result
