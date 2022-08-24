from types import FunctionType
from pydofus2.com.ankamagames.atouin.managers.EntitiesManager import EntitiesManager
from pydofus2.com.ankamagames.dofus import Constants
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.astar.AStar import AStar
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Vertex import Vertex
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.WorldGraph import WorldGraph
from pydofus2.com.ankamagames.atouin.data.map.Cell import Cell
from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from pydofus2.com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.tools.TimeDebug import TimeDebug
from pydofus2.com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray

logger = Logger("Dofus2")


class WorldPathFinder(metaclass=Singleton):

    playedCharacterManager: PlayedCharacterManager

    worldGraph: WorldGraph = None

    callback: FunctionType

    src: Vertex

    dst: float

    linkedZone: int

    def __init__(self):
        self.init()
        super().__init__()

    def init(self) -> None:
        if self.isInitialized():
            return
        self.playedCharacterManager = PlayedCharacterManager()
        with open(Constants.WORLDGRAPH_PATH, "rb") as binaries:
            data = binaries.read()
            self.worldGraph = WorldGraph(ByteArray(data))

    def getWorldGraph(self) -> WorldGraph:
        return self.worldGraph

    def isInitialized(self) -> bool:
        return self.worldGraph is not None

    @property
    def currPlayerVertex(self) -> Vertex:
        if PlayedCharacterManager().currentZoneRp is None or PlayedCharacterManager().currentMap is None:
            return None
        vertex = self.worldGraph.getVertex(
            PlayedCharacterManager().currentMap.mapId, PlayedCharacterManager().currentZoneRp
        )
        return vertex

    def findPath(self, destinationMapId: float, callback: FunctionType, linkedZone: int = 1) -> None:
        if not self.isInitialized():
            callback(None)
            return
        TimeDebug.reset()
        self.src = self.currPlayerVertex
        logger.info(f"Start searching path from {self.currPlayerVertex} to destMapId {destinationMapId}")
        if self.src is None:
            callback(None)
            return
        if linkedZone is None:
            linkedZone = 1
        self.linkedZone = linkedZone
        WorldPathFinder.callback = callback
        self.dst = destinationMapId
        if int(PlayedCharacterManager().currentMap.mapId) == int(self.dst):
            callback([])
            return
        self.next()

    def abortPathSearch(self) -> None:
        AStar.stopSearch()

    def onAStarComplete(self, path: list[Edge]) -> None:
        if path is None:
            self.next()
        else:
            logger.info("path to map " + str(self.dst) + " found in " + str(TimeDebug.getElapsedTime()) + "s")
            self.callback(path)

    def next(self) -> None:
        dstV: Vertex = self.worldGraph.getVertex(self.dst, self.linkedZone)
        self.linkedZone += 1
        if dstV is None:
            logger.info("no path found to map " + str(self.dst))
            cb = self.callback
            self.callback = None
            cb(None)
            return
        AStar.search(self.worldGraph, self.src, dstV, self.onAStarComplete)
