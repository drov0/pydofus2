# from com.ankamagames.atouin.managers.InteractiveCellManager import (
#     InteractiveCellManager,
# )
from com.ankamagames.atouin.data.map.Layer import Layer
from com.ankamagames.atouin.enums.ElementTypesEnum import ElementTypesEnum
from com.ankamagames.atouin.messages.MapLoadedMessage import MapLoadedMessage
from com.ankamagames.jerakine.logger.Logger import Logger
from time import perf_counter
import com.ankamagames.atouin.utils.DataMapProvider as dmpm
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from com.ankamagames.jerakine.types.positions.WorldPoint import WorldPoint

logger = Logger("Dofus2")


class MapDisplayManager(metaclass=Singleton):

    MEMORY_LOG: dict = dict()
    _currentMap: WorldPoint
    _mapInstanceId: float = 0
    _lastMap: WorldPoint
    _nMapLoadStart: int
    _nMapLoadEnd: int
    _identifiedElementPosition: dict[int, MapPoint]
    _currentMapRendered = True

    def __init__(self) -> None:
        from com.ankamagames.jerakine.resources.loaders.MapLoader import MapLoader

        self._loader = MapLoader()
        self._currentMap = None
        self.currentDataMap = None
        self._lastMap = None
        self._nMapLoadStart = 0
        self._nMapLoadEnd = 0
        self._forceReloadWithoutCache = False

    @property
    def dataMap(self):
        return self.currentDataMap

    @property
    def currentMapPoint(self) -> WorldPoint:
        return self._currentMap

    @property
    def mapInstanceId(self) -> float:
        return self._mapInstanceId

    @mapInstanceId.setter
    def mapInstanceId(self, mapId: float) -> None:
        self._mapInstanceId = mapId

    def reset(self) -> None:
        self._currentMap = None
        logger.debug("mapInstanceId reset 0")
        self._mapInstanceId = 0
        self._currentMapRendered = True
        self._lastMap = None

    def initIdentifiedElements(self):
        self._identifiedElementPosition = dict()
        for layer in self.dataMap.layers:
            if layer.layerId == Layer.LAYER_GROUND:
                continue
            for cell in layer.cells:
                for element in cell.elements:
                    if element.elementType == ElementTypesEnum.GRAPHICAL:
                        if element.identifier > 0:
                            self._identifiedElementPosition[element.identifier] = MapPoint.fromCellId(cell.cellId)

    def isIdentifiedElement(self, identifier: int) -> bool:
        return self._identifiedElementPosition.get(identifier)

    def getIdentifiedElementPosition(self, identifier: int) -> MapPoint:
        return self._identifiedElementPosition.get(identifier)

    def mapDisplayed(self) -> None:
        pass

    def loadMap(self, mapId: int, forceReloadWithoutCache: bool = False, decryptionKey=None) -> None:
        from com.ankamagames.dofus.kernel.Kernel import Kernel

        self.lastDataMap = self.currentDataMap
        self._forceReloadWithoutCache = forceReloadWithoutCache
        self._nMapLoadStart = perf_counter()
        map = self._loader.load(mapId, key=decryptionKey)
        self._currentMapRendered = True
        self._nMapLoadEnd = perf_counter()
        logger.debug(f"Map {map.id} loaded in " + str(self._nMapLoadEnd - self._nMapLoadStart) + " seconds")
        dmpm.DataMapProvider().resetUpdatedCell()
        dmpm.DataMapProvider().resetSpecialEffects()
        self.currentDataMap = map
        self._currentMap = WorldPoint.fromMapId(map.id)
        msg = MapLoadedMessage()
        msg.id = self._currentMap.mapId
        self.initIdentifiedElements()
        Kernel().getWorker().process(msg)
