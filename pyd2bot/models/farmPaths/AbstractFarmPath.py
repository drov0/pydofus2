from typing import Iterator
from com.ankamagames.dofus.modules.utils.pathFinding.world.Transition import Transition
from com.ankamagames.dofus.modules.utils.pathFinding.world.Vertex import Vertex
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder


class AbstractFarmPath:
    fightOnly: bool
    _currentVertex: Vertex
    startVertex: Vertex
    skills = []

    def __init__(self) -> None:
        pass

    @property
    def currentVertex(self) -> Transition:
        return WorldPathFinder().currPlayerVertex

    def __next__(self) -> Transition:
        raise NotImplementedError()

    def __in__(self, v: Vertex) -> bool:
        raise NotImplementedError()

    def __iter__(self) -> Iterator[Vertex]:
        raise NotImplementedError()

    def currNeighbors(self) -> Iterator[Vertex]:
        raise NotImplementedError()

    def neighbors(self, vertex: Vertex) -> Iterator[Vertex]:
        raise NotImplementedError()
