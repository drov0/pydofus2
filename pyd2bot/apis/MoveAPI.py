import random
from typing import TYPE_CHECKING

from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import (
    WorldPathFinder,
)

if TYPE_CHECKING:
    from com.ankamagames.atouin.data.map.Map import Map
import com.ankamagames.atouin.managers.MapDisplayManager as mdm
from com.ankamagames.atouin.messages.AdjacentMapClickMessage import (
    AdjacentMapClickMessage,
)
from com.ankamagames.atouin.messages.CellClickMessage import CellClickMessage
from com.ankamagames.atouin.utils.CellIdConverter import CellIdConverter
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.types.enums.DirectionsEnum import DirectionsEnum

logger = Logger(__name__)


class MapChange:
    def __init__(self, mapId, outCellId):
        self.destMapId = mapId
        self.outCellId = outCellId


class MoveAPI:
    @classmethod
    def randomMapChange(cls, discard=[]):
        possibleChangeDirections = cls.getMapChangeDirections(discard)
        if len(possibleChangeDirections) == 0:
            raise Exception("No possible map change direction")
        randomDirection = random.choice(list(possibleChangeDirections.keys()))
        mapChange = possibleChangeDirections[randomDirection]
        logger.debug(
            f"[MouvementAPI] Sending a click to change map towards direction '{randomDirection.name}'"
        )
        cls.sendClickAdjacentMsg(mapChange.destMapId, mapChange.outCellId)
        return mapChange.destMapId

    @classmethod
    def getMapChangeDirections(cls, discard=[]) -> dict[int, MapChange]:
        outgoingDirections = dict()
        currentMap: Map = mdm.MapDisplayManager().dataMap
        playedCharacterManager = PlayedCharacterManager()
        playedEntity = DofusEntities.getEntity(playedCharacterManager.id)
        playedEntityCellId = playedEntity.position.cellId
        v = WorldPathFinder().getCurrentPlayerVertex()
        outgoingEdges = WorldPathFinder().worldGraph.getOutgoingEdgesFromVertex(v)
        for e in outgoingEdges:
            for tr in e.transitions:
                try:
                    direction = DirectionsEnum(tr.direction)
                    destMapId = e.dst.mapId
                    # cellId = currentMap.cellOutTowards(playedEntityCellId, direction)
                    cellId = tr.cell
                    outgoingDirections[direction] = MapChange(destMapId, cellId)
                except ValueError:
                    pass
        return outgoingDirections

    @classmethod
    def changeMapToDirection(cls, direction: DirectionsEnum) -> None:
        mapChange = cls.getMapChangeDirections().get(direction)
        if mapChange is None:
            raise Exception(f"No map found for direction '{direction.name}'")
        cls.sendClickAdjacentMsg(mapChange.destMapId, mapChange.outCellId)

    @classmethod
    def sendClickAdjacentMsg(cls, mapId: float, cellId: int) -> None:
        msg: AdjacentMapClickMessage = AdjacentMapClickMessage()
        msg.cellId = cellId
        msg.adjacentMapId = mapId
        Kernel().getWorker().process(msg)

    @classmethod
    def sendCellClickMsg(cls, mapId: float, cellId: int) -> None:
        msg: CellClickMessage = CellClickMessage()
        msg.cellId = cellId
        msg.id = mapId
        Kernel().getWorker().process(msg)

    @classmethod
    def changeMapToMapdId(cls, destMapId: int) -> None:
        currentMap: Map = mdm.MapDisplayManager().dataMap
        direction = currentMap.getDirectionToNeighbor(destMapId)
        cls.changeMapToDirection(direction)
