import random
from com.ankamagames.atouin.AtouinConstants import AtouinConstants
from com.ankamagames.atouin.data.map.Cell import Cell
from typing import TYPE_CHECKING

from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldGraph import WorldGraph
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import (
    WorldPathFinder,
)
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity

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


class FrustumManager:
    @classmethod
    def randomMapChange(cls, discard=[]):
        possibleChangeDirections = cls.getMapChangeDirections(discard)
        randomDirection = random.choice(list(possibleChangeDirections.keys()))
        mapChange = possibleChangeDirections[randomDirection]
        logger.debug(
            f"[MouvementAPI] Sending a click to change map towards direction '{randomDirection.name}'"
        )
        cls.sendClickAdjacentMsg(mapChange.destMapId, mapChange.outCellId)
        return mapChange.destMapId

    @classmethod
    def getMapChangeDirections(cls, discard=[]):
        currentMap: Map = mdm.MapDisplayManager().dataMap
        playedCharacterManager = PlayedCharacterManager()
        playedEntity = DofusEntities.getEntity(playedCharacterManager.id)
        playedEntityCellId = playedEntity.position.cellId
        result = dict[DirectionsEnum, MapChange]()
        for direction in DirectionsEnum.getMapChangeDirections():
            destMapId = currentMap.getNeighborIdFromDirection(direction)
            if destMapId in discard:
                continue
            cellId = currentMap.cellOutTowards(playedEntityCellId, direction)
            if cellId is not None:
                result[direction] = MapChange(destMapId, cellId)
        return result

    @classmethod
    def getTransitionByDirection(cls, direction):
        playedEntity: IEntity = DofusEntities.getEntity(PlayedCharacterManager().id)
        if not playedEntity:
            raise Exception("No entity found for player")
        playedEntityCellId: int = playedEntity.position.cellId
        playerCell: Cell = mdm.MapDisplayManager().dataMap.cells[playedEntityCellId]
        currentMap: Map = mdm.MapDisplayManager().dataMap
        currVertex = WorldPathFinder().worldGraph.getVertex(
            currentMap.id, playerCell.linkedZoneRP
        )
        outgoingEdges = WorldPathFinder().worldGraph.getOutgoingEdgesFromVertex(
            currVertex
        )
        for edge in outgoingEdges:
            for tr in edge.transitions:
                if DirectionsEnum(tr.direction) == direction:
                    return edge.dst.mapId, tr.cell
        return None, None

    @classmethod
    def changeMapToDirection(cls, direction: DirectionsEnum) -> None:
        destMapId, cellId = cls.getTransitionByDirection(direction)
        if destMapId is None:
            raise Exception("No map found for direction " + direction.name)
        if cellId is not None:
            logger.debug(
                f"[MouvementAPI] change Map To Direction  '{direction.name}'"
            )
            cls.sendClickAdjacentMsg(destMapId, cellId)
        else:
            logger.warn(
                "[MouvementAPI] Unable to change map to direction " + str(direction)
            )

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
