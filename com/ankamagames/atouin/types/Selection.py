from tokenize import Floatnumber
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)


class Selection:
    _mapId: Floatnumber

    cells: list[int]

    cellId: int

    visible: bool

    def __init__(self):
        super().__init__()

    @property
    def mapId(self) -> float:
        if self._mapId is None:
            return MapDisplayManager().currentMapPoint.mapId
        return self._mapId

    @mapId.setter
    def mapId(self, id: float) -> None:
        self._mapId = id

    def update(self, pUpdateStrata: bool = False) -> None:
        self.visible = True

    def remove(self, aCells: list[int] = None) -> None:
        if self.renderer:
            if not aCells or aCells == self.cells:
                self.visible = False
            else:
                pass

    def isInside(self, cellId: int) -> bool:
        return cellId in self.cells
