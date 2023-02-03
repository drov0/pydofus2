from pydofus2.com.ankamagames.jerakine.map.IDataMapProvider import \
    IDataMapProvider
from pydofus2.com.ankamagames.jerakine.map.ILosDetector import ILosDetector
from pydofus2.com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from pydofus2.mapTools import MapTools


class LosDetector(ILosDetector):
    _tested = dict[MapPoint, dict[MapPoint, bool]]()
    
    @classmethod
    def losBetween(
        cls, mapProvider: IDataMapProvider, refPos: MapPoint, targetPos: MapPoint, tested: dict[str, bool] = {}
    ) -> bool:
        if targetPos in tested:
            return tested[targetPos]
        line = MapTools.getCellsCoordBetween(refPos.cellId, targetPos.cellId)
        if len(line) == 0:
            los = True
        else:
            los = True
            for j in range(len(line) - 1):
                if MapPoint.isInMap(line[j].x, line[j].y):
                    if j > 0 and mapProvider.hasEntity(line[j - 1].x, line[j - 1].y, False):
                        los = False
                    elif targetPos not in tested:
                        los = los and mapProvider.pointLos(line[j].x, line[j].y, False)
                    else:
                        los = los and tested[targetPos]
                    if not los:
                        break
        tested[targetPos] = los
        return los

    @classmethod
    def getCells(cls, mapProvider: IDataMapProvider, spellrange: list[int], refPosition: int) -> set[int]:
        refPosition = MapPoint.fromCellId(refPosition)
        orderedCell: list = list()
        for cellId in spellrange:
            mp = MapPoint.fromCellId(cellId)
            orderedCell.append({"p": mp, "dist": refPosition.distanceToCell(mp)})
        orderedCell.sort(key=lambda x: x["dist"], reverse=True)
        if refPosition not in cls._tested:
            cls._tested[refPosition] = dict[MapPoint, bool]()
        result = set[int]()
        for i in range(len(orderedCell)):
            p: MapPoint = orderedCell[i]["p"]
            if p not in cls._tested[refPosition]:
                line = MapTools.getCellsCoordBetween(refPosition.cellId, p.cellId)
                if len(line) == 0:
                    result.add(p.cellId)
                else:
                    los = True
                    for j in range(len(line) - 1):
                        if MapPoint.isInMap(line[j].x, line[j].y):
                            if j > 0 and mapProvider.hasEntity(line[j - 1].x, line[j - 1].y, False):
                                los = False
                            elif line[j] not in cls._tested[refPosition]:
                                los = los and mapProvider.pointLos(line[j].x, line[j].y, False)
                            else:
                                los = los and cls._tested[refPosition][line[j]]
                        if not los:
                            break
                    cls._tested[refPosition][p] = los
        for i in spellrange:
            mp = MapPoint.fromCellId(i)
            result = {mp.cellId for mp in cls._tested[refPosition] if cls._tested[refPosition][mp]}
        return result
    
    @classmethod
    def clearCache(cls):
        cls._tested.clear()