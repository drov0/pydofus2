from types import FunctionType
from com.ankamagames.atouin.managers.EntitiesManager import EntitiesManager
from com.ankamagames.dofus import Constants
from com.ankamagames.dofus.modules.utils.pathFinding.astar.AStar import AStar
from com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge
from com.ankamagames.dofus.modules.utils.pathFinding.world.Vertex import Vertex
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldGraph import WorldGraph
from com.ankamagames.atouin.data.map.Cell import Cell
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.modules.utils.pathFinding.tools.TimeDebug import TimeDebug
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray

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

    def getCurrentPlayerVertex(self) -> Vertex:
        playedEntity: IEntity = DofusEntities.getEntity(PlayedCharacterManager().id)
        if playedEntity is None:
            logger.error("No player entity found")
            return None
        playedEntityCellId: int = playedEntity.position.cellId
        playerCell: Cell = MapDisplayManager().dataMap.cells[playedEntityCellId]
        vertex = self.worldGraph.getVertex(PlayedCharacterManager().currentMap.mapId, playerCell.linkedZoneRP)
        return vertex

    def findPath(self, destinationMapId: float, callback: FunctionType) -> None:
        if not self.isInitialized():
            callback(None)
            return
        logger.info("Start searching path to " + str(destinationMapId))
        TimeDebug.reset()
        self.src = self.getCurrentPlayerVertex()
        if self.src is None:
            callback(None)
            return
        self.linkedZone = 1
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
