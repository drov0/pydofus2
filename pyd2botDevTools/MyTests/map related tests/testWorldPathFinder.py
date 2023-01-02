from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.astar.AStar import AStar
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder


dstmapId = 193331718
dstMapRpz = 1

srcMapId = 193331717.0
srcMapRpz = 3

MapDisplayManager().loadMap(srcMapId)

dstV = WorldPathFinder().worldGraph.getVertex(dstmapId, dstMapRpz)
srcV = WorldPathFinder().worldGraph.getVertex(srcMapId, dstMapRpz)

vs = WorldPathFinder().worldGraph.getVertices(srcMapId)
for k, v in vs.items():
    print(f"Vertex {v}")
    
oev = WorldPathFinder().worldGraph.getOutgoingEdgesFromVertex(srcV)
for e in oev:
    print(f"|- src {e.src} -> dst ({e.dst})")
    for tr in e.transitions:
        print(f"\t|- direction : {tr.direction}, skill : {tr.skillId}, cell : {tr.cell}, type : {tr.type}")
path = AStar.search(WorldPathFinder().worldGraph, srcV, dstV, lambda x: (), False)
if path is None:
    print("No path found")
else:
    for e in path:
        print(f"|- src {e.src} -> dst ({e.dst})")
        for tr in e.transitions:
            print(f"\t|- direction : {tr.direction}, skill : {tr.skillId}, cell : {tr.cell}, type : {tr.type}")