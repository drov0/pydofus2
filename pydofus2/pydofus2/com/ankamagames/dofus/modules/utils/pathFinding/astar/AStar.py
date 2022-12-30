from time import perf_counter
from types import FunctionType
from pydofus2.com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.TransitionTypeEnum import TransitionTypeEnum
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
from pydofus2.com.ankamagames.jerakine.utils.display.EnterFrameConst import EnterFrameConst
from pydofus2.com.ankamagames.jerakine.utils.display.EnterFrameDispatcher import (
    EnterFrameDispatcher,
)

logger = Logger("Dofus2")


class AStar:
    DEBUG = False

    dest: MapPosition = None

    closedDic = dict()

    openList = list[Node]()

    openDic = dict()

    iterations: int = 0

    worldGraph: WorldGraph = None

    dst: Vertex = None

    callback: FunctionType = None

    _forbiddenSubareaIds = list[int]()

    HEURISTIC_SCALE: int = 1

    INDOOR_WEIGHT: int = 0

    MAX_ITERATION: int = 10000

    
    def __init__(self):
        super().__init__()

    @classmethod
    def search(cls, worldGraph: WorldGraph, src: Vertex, dst: Vertex, callback: FunctionType, onFrame=True) -> list["Edge"]:
        logger.info(f"Searching path from {src} to {dst} ...")
        if cls.callback != None:
            raise Exception("Pathfinding already in progress")
        if src == dst:
            callback(None)
            return
        cls.initForbiddenSubareaList()
        cls.worldGraph = worldGraph
        cls.dst = dst
        cls.callback = callback
        cls.dest = MapPosition.getMapPositionById(dst.mapId)
        cls.closedDic = dict()
        cls.openList = list[Node]()
        cls.openDic = dict()
        cls.iterations = 0
        cls.openList.append(Node(src, MapPosition.getMapPositionById(src.mapId)))
        if not onFrame:
            return cls.compute()
        EnterFrameDispatcher().addEventListener(cls.compute, EnterFrameConst.COMPUTE_ASTAR)

    @classmethod
    def initForbiddenSubareaList(cls) -> None:
        cls._forbiddenSubareaIds = GameDataQuery.queryEquals(SubArea, "mountAutoTripAllowed", False)

    @classmethod
    def stopSearch(cls) -> None:
        if cls.callback != None:
            cls.callbackWithResult(None)

    @classmethod
    def compute(cls, e: Event = None) -> None:
        while cls.openList:
            if cls.DEBUG:
                logger.debug(f"Iteration {cls.iterations}")
            if cls.iterations > cls.MAX_ITERATION:
                cls.callbackWithResult(None)
                logger.error("Too many iterations, aborting A*")
                return None
            cls.iterations += 1
            current = cls.openList.pop(0)
            cls.openDic[current.vertex] = None
            if current.vertex == cls.dst:
                logger.info("Goal reached within " + str(cls.iterations) + " iterations")
                result = cls.buildResultPath(cls.worldGraph, current)
                cls.callbackWithResult(result)
                return result
            edges = cls.worldGraph.getOutgoingEdgesFromVertex(current.vertex)
            oldLength = len(cls.openList)
            cost = current.cost + 1
            for edge in edges:
                if cls.hasValidTransition(edge):
                    if cls.hasValidDestinationSubarea(edge):
                        existing = cls.closedDic.get(edge.dst)
                        if not (existing != None and cost >= existing.cost):
                            existing = cls.openDic.get(edge.dst)
                            if not (existing != None and cost >= existing.cost):
                                map = MapPosition.getMapPositionById(edge.dst.mapId)
                                if map == None:
                                    logger.info(f"The map {edge.dst.mapId} doesn't seem to exist")
                                else:
                                    manhattanDistance = abs(map.posX - cls.dest.posX) + abs(map.posY - cls.dest.posY)
                                    node = Node(
                                        edge.dst,
                                        map,
                                        cost,
                                        cost
                                        + cls.HEURISTIC_SCALE * manhattanDistance
                                        + (cls.INDOOR_WEIGHT if current.map.outdoor and not map.outdoor else 0),
                                        current,
                                    )
                                    cls.openList.append(node)
                                    cls.openDic[node.vertex] = node
            cls.closedDic[current.vertex] = current
            if oldLength < len(cls.openList):
                cls.openList.sort(key=lambda x: x.heuristic)
        cls.callbackWithResult(None)
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
            if edge.src.mapId == PlayedCharacterManager().currentMap.mapId and transition.type == TransitionTypeEnum.SCROLL.value:
                srcCell = PlayedCharacterManager().entity.position
                dstCell = MapPoint.fromCellId(transition.cell)
                movePath = Pathfinding.findPath(DataMapProvider(), srcCell, dstCell)
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

    @classmethod
    def hasValidDestinationSubarea(cls, edge: Edge) -> bool:
        fromMapId: float = edge.src.mapId
        fromSubareaId: int = MapPosition.getMapPositionById(fromMapId).subAreaId
        toMapId: float = edge.dst.mapId
        toSubareaId: int = MapPosition.getMapPositionById(toMapId).subAreaId
        if fromSubareaId == toSubareaId:
            return True
        return toSubareaId not in cls._forbiddenSubareaIds

    @classmethod
    def callbackWithResult(cls, result: list[Edge]) -> None:
        cb: FunctionType = cls.callback
        cls.callback = None
        EnterFrameDispatcher().removeEventListener(cls.compute)
        cb(result)

    @classmethod
    def orderNodes(cls, a: Node, b: Node) -> int:
        return 0 if a.heuristic == b.heuristic else (1 if a.heuristic > b.heuristic else -1)

    @classmethod
    def buildResultPath(cls, worldGraph: WorldGraph, node: Node) -> list[Edge]:
        result = list[Edge]()
        while node.parent != None:
            result.append(worldGraph.getEdge(node.parent.vertex, node.vertex))
            node = node.parent
        result.reverse()
        return result
