import random
from com.ankamagames.atouin.AtouinConstants import AtouinConstants
from com.ankamagames.atouin.data.map.Cell import Cell
from typing import TYPE_CHECKING

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
    def changeMapToDirection(cls, direction: DirectionsEnum) -> None:
        currentMap: Map = mdm.MapDisplayManager().dataMap
        destMapId = currentMap.getNeighborIdFromDirection(direction)
        playedCharacterManager = PlayedCharacterManager()
        playedEntity = DofusEntities.getEntity(playedCharacterManager.id)
        playedEntityCellId = playedEntity.position.cellId
        cellId = currentMap.cellOutTowards(playedEntityCellId, direction)
        if cellId is not None:
            logger.debug(
                f"[MouvementAPI] FrustumManager.changeMapToDirection  = {direction.name}"
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
