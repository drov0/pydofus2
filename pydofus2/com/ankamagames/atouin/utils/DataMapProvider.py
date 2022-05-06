from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.atouin.AtouinConstants import AtouinConstants
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.atouin.data.map.Cell import Cell
import com.ankamagames.atouin.managers.MapDisplayManager as mdmm
from com.ankamagames.atouin.managers.EntitiesManager import EntitiesManager
from com.ankamagames.jerakine.interfaces.IObstacle import IObstacle
from com.ankamagames.jerakine.map.IDataMapProvider import IDataMapProvider
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from mapTools import MapTools

logger = Logger("pyd2bot")


class DataMapProvider(IDataMapProvider, metaclass=Singleton):
    TOLERANCE_ELEVATION: int = 11
    obstaclesCells = list[int]()
    _updatedCell = dict()
    _specialEffects = dict()
    _playerobject = None
    isInFight = False

    def __init__(self):
        super().__init__()

    def init(self, playerobject: object):
        self._playerobject = playerobject

    def pointLos(self, x: int, y: int, bAllowTroughEntity: bool = True) -> bool:
        cellId: int = MapTools.getCellIdByCoord(x, y)
        los: bool = mdmm.MapDisplayManager().currentDataMap.cells[cellId].los
        if self._updatedCell.get(cellId):
            los = self._updatedCell[cellId]
        if not bAllowTroughEntity:
            cellEntities = EntitiesManager().getEntitiesOnCell(cellId, IObstacle)
            if len(cellEntities):
                for o in cellEntities:
                    if not o.canSeeThrough:
                        return False
        return los

    def farmCell(self, x: int, y: int) -> bool:
        cellId: int = MapTools.getCellIdByCoord(x, y)
        return mdmm.MapDisplayManager().currentDataMap.cells[cellId].farmCell

    def cellByIdIsHavenbagCell(self, cellId: int) -> bool:
        return mdmm.MapDisplayManager().currentDataMap.cells[cellId].havenbagCell

    def cellByCoordsIsHavenbagCell(self, x: int, y: int) -> bool:
        cellId: int = MapTools.getCellIdByCoord(x, y)
        return mdmm.MapDisplayManager().currentDataMap.cells[cellId].havenbagCell

    def isChangeZone(self, cell1: int, cell2: int) -> bool:
        cellData1: "Cell" = mdmm.MapDisplayManager().currentDataMap.cells[cell1]
        cellData2: "Cell" = mdmm.MapDisplayManager().currentDataMap.cells[cell2]
        dif: int = abs(abs(cellData1.floor) - abs(cellData2.floor))
        return cellData1.moveZone != cellData2.moveZone and dif == 0

    def pointMov(
        self,
        x: int,
        y: int,
        bAllowTroughEntity: bool = True,
        previousCellId: int = -1,
        endCellId: int = -1,
        avoidObstacles: bool = True,
        dataMap=None,
    ) -> bool:
        if MapPoint.isInMap(x, y):
            if dataMap is None:
                dataMap = mdmm.MapDisplayManager().dataMap
            useNewSystem = dataMap.isUsingNewMovementSystem
            cellId = MapTools.getCellIdByCoord(x, y)
            cellData = dataMap.cells[cellId]
            mov = cellData.mov and not (self.isInFight and cellData.nonWalkableDuringFight)
            if self._updatedCell.get(cellId) != None:
                mov = self._updatedCell[cellId]
            if mov and useNewSystem and previousCellId != -1 and previousCellId != cellId:
                previousCellData = dataMap.cells[previousCellId]
                dif = abs(abs(cellData.floor) - abs(previousCellData.floor))
                if (
                    previousCellData.moveZone != cellData.moveZone
                    and dif > 0
                    or previousCellData.moveZone == cellData.moveZone
                    and cellData.moveZone == 0
                    and dif > self.TOLERANCE_ELEVATION
                ):
                    mov = False
            if not bAllowTroughEntity:
                # logger.debug(f"avoiding through entity {list(EntitiesManager().entities.keys())}")
                for e in EntitiesManager().entities.values():
                    if isinstance(e, IObstacle) and e.position and e.position.cellId == cellId:
                        if not (endCellId == cellId and e.canWalkTo):
                            if not e.canWalkThrough:
                                return False
                if avoidObstacles and (cellId in self.obstaclesCells and cellId != endCellId):
                    return False
        else:
            mov = False
        return mov

    def pointCanStop(self, x: int, y: int, bAllowTroughEntity: bool = True) -> bool:
        cellId: int = MapTools.getCellIdByCoord(x, y)
        cellData: "Cell" = mdmm.MapDisplayManager().currentDataMap.cells[cellId]
        return self.pointMov(x, y, bAllowTroughEntity) and (self.isInFight or not cellData.nonWalkableDuringRP)

    def fillEntityOnCellArray(self, v: list[bool], allowThroughEntity: bool) -> list[bool]:
        for e in EntitiesManager().entities.values():
            if (
                isinstance(e, self._playerobject)
                and (not allowThroughEntity or not e.canWalkThrough)
                and e.position is not None
            ):
                v[e.position.cellId] = True
        return v

    def pointWeight(self, x: int, y: int, bAllowTroughEntity: bool = True) -> float:
        weight: float = 1
        cellId: int = MapTools.getCellIdByCoord(x, y)
        speed: int = self.getCellSpeed(cellId)
        if bAllowTroughEntity:
            if speed >= 0:
                weight += 5 - speed
            else:
                weight += 11 + abs(speed)
            entity = EntitiesManager().getEntityOnCell(cellId, self._playerobject)
            if entity:
                weight = 20
            else:
                if EntitiesManager().getEntityOnCell(cellId, self._playerobject) is not None:
                    weight += 0.3
                if (
                    EntitiesManager().getEntityOnCell(MapTools.getCellIdByCoord(x + 1, y), self._playerobject)
                    is not None
                ):
                    weight += 0.3
                if (
                    EntitiesManager().getEntityOnCell(MapTools.getCellIdByCoord(x, y + 1), self._playerobject)
                    is not None
                ):
                    weight += 0.3
                if (
                    EntitiesManager().getEntityOnCell(MapTools.getCellIdByCoord(x - 1, y), self._playerobject)
                    is not None
                ):
                    weight += 0.3
                if (
                    EntitiesManager().getEntityOnCell(MapTools.getCellIdByCoord(x, y - 1), self._playerobject)
                    is not None
                ):
                    weight += 0.3
                if (self.pointSpecialEffects(x, y) & 2) == 2:
                    weight += 0.2
        return weight

    def getCellSpeed(self, cellId: int) -> int:
        return mdmm.MapDisplayManager().currentDataMap.cells[cellId].speed

    def pointSpecialEffects(self, x: int, y: int) -> int:
        cellId: int = MapTools.getCellIdByCoord(x, y)
        if self._specialEffects.get(cellId):
            return self._specialEffects[cellId]
        return 0

    @property
    def width(self) -> int:
        return AtouinConstants.MAP_HEIGHT + AtouinConstants.MAP_WIDTH - 2

    @property
    def height(self) -> int:
        return AtouinConstants.MAP_HEIGHT + AtouinConstants.MAP_WIDTH - 1

    def hasEntity(self, x: int, y: int, bAllowTroughEntity: bool = False) -> bool:
        cellEntities: list[IObstacle] = EntitiesManager().getEntitiesOnCell(MapTools.getCellIdByCoord(x, y), IObstacle)
        for o in cellEntities:
            if not (o.canWalkTo or (bAllowTroughEntity and o.canSeeThrough)):
                return True
        return False

    def updateCellMovLov(self, cellId: int, canMove: bool) -> None:
        self._updatedCell[cellId] = canMove

    def resetUpdatedCell(self) -> None:
        self._updatedCell = dict()

    def setSpecialEffects(self, cellId: int, value: int) -> None:
        self._specialEffects[cellId] = value

    def resetSpecialEffects(self) -> None:
        self._specialEffects = dict()
