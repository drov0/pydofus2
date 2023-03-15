from time import perf_counter
from pydofus2.com.ankamagames.dofus import Constants
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Vertex import Vertex
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.ThreadSharedSingleton import ThreadSharedSingleton
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray

class WorldGraph(metaclass=ThreadSharedSingleton):
    
    def __init__(self):
        self._vertices = dict[int, dict[int, Vertex]]()
        self._edges = dict[float, Edge]()
        self._outgoingEdges = dict[float, list[Edge]]()
        self._vertexUid: float = 0
        self.init()

    def init(self):
        s = perf_counter()
        with open(Constants.WORLDGRAPH_PATH, "rb") as binaries:
            data = ByteArray(binaries.read())
            edgeCount: int = data.readInt()
            for _ in range(edgeCount):
                src = self.addVertex(data.readDouble(), data.readInt())
                dest = self.addVertex(data.readDouble(), data.readInt())
                edge = self.addEdge(src, dest)
                transitionCount = data.readInt()
                for _ in range(transitionCount):
                    edge.addTransition(
                        data.readByte(),
                        data.readByte(),
                        data.readInt(),
                        data.readUTFBytes(data.readInt()),
                        data.readDouble(),
                        data.readInt(),
                        data.readDouble(),
                    )
            del data
        Logger().debug("WorldGraph loaded in %s seconds", perf_counter() - s)

    def addEdge(self, src: Vertex, dest: Vertex) -> Edge:
        edge: Edge = self._edges.get(src.UID, {}).get(dest.UID)
        if edge:
            return edge
        if not self.doesVertexExist(src) or not self.doesVertexExist(dest):
            return None
        edge = Edge(src, dest)
        if self._edges.get(src.UID) is None:
            self._edges[src.UID] = dict()
        self._edges[src.UID][dest.UID] = edge
        outgoing = self._outgoingEdges.get(src.UID)
        if outgoing is None:
            outgoing = list[Edge]()
            self._outgoingEdges[src.UID] = outgoing
        outgoing.append(edge)
        return edge

    def addVertex(self, mapId: float, zone: int) -> Vertex:
        vertex: Vertex = self._vertices.get(mapId, {}).get(zone)
        if vertex is None:
            vertex = Vertex(mapId, zone, self._vertexUid)
            self._vertexUid += 1
            if mapId not in self._vertices:
                self._vertices[mapId] = dict()
            self._vertices[mapId][zone] = vertex
        return vertex
    
    def doesVertexExist(self, v: Vertex) -> bool:
        return v.mapId in self._vertices and v.zoneId in self._vertices[v.mapId]
    
    def getEdges(self) -> dict:
        return self._edges

    def getVertex(self, mapId: float, mapRpZone: int) -> Vertex:
        mapId = float(mapId)
        mapRpZone = int(mapRpZone)
        return self._vertices.get(mapId, {}).get(mapRpZone)

    def getVertices(self, mapId) -> dict[int, Vertex]:
        return self._vertices.get(mapId)

    def getOutgoingEdgesFromVertex(self, src: Vertex) -> list[Edge]:
        return self._outgoingEdges.get(src.UID, [])

    def getEdge(self, src: Vertex, dest: Vertex) -> Edge:
        return self._edges.get(src.UID, {}).get(dest.UID)
        
    def reset(self):
        self._vertices.clear()
        self._edges.clear()
        self._outgoingEdges.clear()
        self._vertexUid: float = 0