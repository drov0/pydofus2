import collections
import random
from typing import Iterator
from com.ankamagames.dofus.datacenter.world.SubArea import SubArea
from com.ankamagames.dofus.modules.utils.pathFinding.astar.AStar import AStar
from com.ankamagames.dofus.modules.utils.pathFinding.world.Transition import Transition
from com.ankamagames.dofus.modules.utils.pathFinding.world.Vertex import Vertex
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder
from pyd2bot.models.farmPaths.AbstractFarmPath import AbstractFarmPath


class RandomSubAreaFarmPath(AbstractFarmPath):
    def __init__(self, subAreaId: int, startVertex: Vertex, fightOnly: bool = False, monsterLvlCoefDiff : float = float("inf")) -> None:
        self.fightOnly = fightOnly
        self.startVertex = startVertex
        self.subArea = SubArea.getSubAreaById(subAreaId)
        self._currentVertex = None
        self._verticies = list[Vertex]()
        self.monsterLvlCoefDiff = monsterLvlCoefDiff

    def __next__(self) -> Transition:
        outgoingEdges = WorldPathFinder().worldGraph.getOutgoingEdgesFromVertex(self.currentVertex)
        transitions = []
        for edge in outgoingEdges:
            if edge.dst.mapId in self.subArea.mapIds:
                if AStar.hasValidTransition(edge):
                    for tr in edge.transitions:
                        if tr.direction != -1:
                            transitions.append(tr)
        return random.choice(transitions)

    def currNeighbors(self) -> Iterator[Vertex]:
        return self.neighbors(self.currentVertex)

    def neighbors(self, vertex: Vertex) -> Iterator[Vertex]:
        outgoingEdges = WorldPathFinder().worldGraph.getOutgoingEdgesFromVertex(vertex)
        for edge in outgoingEdges:
            if edge.dst.mapId in self.subArea.mapIds:
                found = False
                for tr in edge.transitions:
                    if tr.direction != -1:
                        found = True
                        break
                if found:
                    yield edge.dst

    @property
    def verticies(self):
        if self._verticies:
            return self._verticies
        queue = collections.deque([self.startVertex])
        self._verticies = set([self.startVertex])
        while queue:
            curr = queue.popleft()
            for v in self.neighbors(curr):
                if v not in self._verticies:
                    queue.append(v)
                    self._verticies.add(v)
        return self._verticies

    def __iter__(self) -> Iterator[Vertex]:
        for it in self.verticies:
            yield it

    def __in__(self, vertex: Vertex) -> bool:
        return vertex in self.verticies
