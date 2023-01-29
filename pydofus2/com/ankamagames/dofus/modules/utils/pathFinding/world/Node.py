from pydofus2.com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Vertex import Vertex

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.astar.AStar import AStar


class Node:
    HEURISTIC_SCALE: int = 1
    INDOOR_WEIGHT: int = 0
    MAX_ITERATION: int = 10000

    def __init__(
        self,
        astar: "AStar",
        vertex: Vertex,
        parent: "Node" = None,
    ):
        self.parent = parent
        self.map = MapPosition.getMapPositionById(vertex.mapId)
        self.moveCost = 0
        self.heuristic = 0
        if parent is not None:
            self.moveCost = parent.moveCost + 1
            manhattanDistance = abs(self.map.posX - astar.dstMap.posX) + abs(self.map.posY - astar.dstMap.posY)
            self.heuristic = self.HEURISTIC_SCALE * manhattanDistance + (
                astar.INDOOR_WEIGHT if parent.map.outdoor and not self.map.outdoor else 0
            )
        self.totalCost = self.moveCost + self.heuristic
        self.vertex = vertex
        self.closed = False
        self.mapId = vertex.mapId
