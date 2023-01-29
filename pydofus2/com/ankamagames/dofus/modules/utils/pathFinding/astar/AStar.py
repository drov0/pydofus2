import heapq
from time import perf_counter
from types import FunctionType
from pydofus2.com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.TransitionTypeEnum import TransitionTypeEnum
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.pathfinding.Pathfinding import Pathfinding
from pydofus2.com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from whistle import Event
from pydofus2.com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition
from pydofus2.com.ankamagames.dofus.datacenter.world.SubArea import SubArea
from pydofus2.com.ankamagames.dofus.misc.utils.GameDataQuery import GameDataQuery
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Node import Node
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Vertex import Vertex
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.WorldGraph import WorldGraph
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger


class AStar(metaclass=Singleton):
    DEBUG = False
    _forbiddenSubareaIds = list[int]()
    HEURISTIC_SCALE: int = 1
    INDOOR_WEIGHT: int = 0
    MAX_ITERATION: int = 10000

    def __init__(self):
        super().__init__()
        self.openList = list[Node]()
        self.openDic = dict()
        self.iterations: int = 0
        self.worldGraph: WorldGraph = None
        self.dst: Vertex = None
        self.callback: FunctionType = None

    def search(
        self, worldGraph: WorldGraph, src: Vertex, dst: Vertex, callback: FunctionType, onFrame=True
    ) -> list["Edge"]:
        Logger().info(f"Searching path from {src} to {dst} ...")
        if self.callback != None:
            raise Exception("Pathfinding already in progress")
        if src == dst:
            callback(None)
            return
        self.initForbiddenSubareaList()
        self.worldGraph = worldGraph
        self.dst = dst
        self.dstMap = MapPosition.getMapPositionById(self.dst.mapId)
        self.callback = callback
        self.openList = list[tuple[int, Node]]()
        self.openDic = dict[Vertex, Node]()
        self.iterations = 0
        node = Node(self, src)
        heapq.heappush(self.openList, (0, id(node), node))
        return self.compute()

    def initForbiddenSubareaList(self) -> None:
        self._forbiddenSubareaIds = GameDataQuery.queryEquals(SubArea, "mountAutoTripAllowed", False)

    def stopSearch(self) -> None:
        if self.callback != None:
            self.callbackWithResult(None)

    def compute(self, e: Event = None) -> None:
        s = perf_counter()
        while self.openList:
            self.iterations += 1
            _, _, current = heapq.heappop(self.openList)
            if current.closed:
                continue
            current.closed = True
            if current.vertex == self.dst:
                Logger().info(f"Goal reached within {self.iterations} iterations and {perf_counter() - s} seconds")
                result = self.buildResultPath(self.worldGraph, current)
                self.callbackWithResult(result)
                return result
            edges = self.worldGraph.getOutgoingEdgesFromVertex(current.vertex)
            for edge in edges:
                if self.hasValidTransition(edge) and self.hasValidDestinationSubarea(edge):
                    existing = self.openDic.get(edge.dst)
                    if existing is None or current.moveCost + 1 < existing.moveCost:
                        node = Node(self, edge.dst, current)
                        self.openDic[edge.dst] = node
                        heapq.heappush(self.openList, (node.totalCost, id(node), node))
        Logger().info(f"Goal not reached within {self.iterations} iterations")
        self.callbackWithResult(None)
        return None

    @staticmethod
    def hasValidTransition(edge: Edge) -> bool:
        from pydofus2.com.ankamagames.dofus.datacenter.items.criterion.GroupItemCriterion import (
            GroupItemCriterion,
        )

        criterionWhiteList: list = [
            "Ad",
            "DM",
            "MI",
            "Mk",
            "Oc",
            "Pc",
            "QF",
            "Qo",
            "Qs",
            "Sv",
        ]
        valid: bool = False
        canUseTr = True
        for transition in edge.transitions:
            canUseTr = True
            if (
                edge.src.mapId == PlayedCharacterManager().currentMap.mapId
                and TransitionTypeEnum(transition.type) == TransitionTypeEnum.SCROLL
            ):
                srcCell = PlayedCharacterManager().entity.position
                dstCell = MapPoint.fromCellId(transition.cell)
                movePath = Pathfinding().findPath(DataMapProvider(), srcCell, dstCell)
                if movePath.end.cellId != dstCell.cellId:
                    canUseTr = False
            if len(transition.criterion) != 0:
                if (
                    "&" not in transition.criterion
                    and "|" not in transition.criterion
                    and transition.criterion[0:2] not in criterionWhiteList
                ):
                    return False
                criterion = GroupItemCriterion(transition.criterion)
                if not criterion.isRespected:
                    return False
                elif canUseTr:
                    return True
            valid = canUseTr
        return valid

    def hasValidDestinationSubarea(self, edge: Edge) -> bool:
        fromMapId: float = edge.src.mapId
        fromSubareaId: int = MapPosition.getMapPositionById(fromMapId).subAreaId
        toMapId: float = edge.dst.mapId
        toSubareaId: int = MapPosition.getMapPositionById(toMapId).subAreaId
        if fromSubareaId == toSubareaId:
            return True
        return toSubareaId not in self._forbiddenSubareaIds

    def callbackWithResult(self, result: list[Edge]) -> None:
        cb: FunctionType = self.callback
        self.callback = None
        cb(result)

    def orderNodes(self, a: Node, b: Node) -> int:
        return 0 if a.heuristic == b.heuristic else (1 if a.heuristic > b.heuristic else -1)

    def buildResultPath(self, worldGraph: WorldGraph, node: Node) -> list[Edge]:
        result = list[Edge]()
        while node.parent is not None:
            result.append(worldGraph.getEdge(node.parent.vertex, node.vertex))
            node = node.parent
        result.reverse()
        return result
