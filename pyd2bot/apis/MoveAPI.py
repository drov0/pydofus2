import random
from typing import TYPE_CHECKING, Tuple
from com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition

from com.ankamagames.dofus.modules.utils.pathFinding.world.Transition import Transition

from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import (
    WorldPathFinder,
)

if TYPE_CHECKING:
    from com.ankamagames.atouin.data.map.Map import Map
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import (
        RoleplayInteractivesFrame,
    )
import com.ankamagames.atouin.managers.MapDisplayManager as mdm
from com.ankamagames.atouin.messages.AdjacentMapClickMessage import (
    AdjacentMapClickMessage,
)
from com.ankamagames.atouin.messages.CellClickMessage import CellClickMessage
from com.ankamagames.dofus.kernel.Kernel import Kernel
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
        transitions = cls.getOutGoingTransitions(discard)
        if len(transitions) == 0:
            raise Exception("Nbr of possible map change direction")
        logger.debug("Nbr of Possible directions: %d", len(transitions))
        randTransition = random.choice(transitions)
        if randTransition.skillId > 0:
            rplInteractivesFrame: "RoleplayInteractivesFrame" = (
                Kernel().getWorker().getFrame("RoleplayInteractivesFrame")
            )
            ie = rplInteractivesFrame.interactives.get(randTransition.id)
            if ie is None:
                raise Exception(
                    f"[MouvementAPI] InteractiveElement {randTransition.id} not found"
                )
            logger.debug(
                f"[MouvementAPI] Activating skill {randTransition.skillId} to change map towards '{randTransition.transitionMapId}'"
            )
            rplInteractivesFrame.skillClicked(ie)
        else:
            logger.debug(
                f"[MouvementAPI] Sending a click to change map towards direction '{randTransition.transitionMapId}'"
            )
            cls.sendClickAdjacentMsg(
                randTransition.transitionMapId, randTransition.cell
            )
        return randTransition.transitionMapId, randTransition.skillId

    @classmethod
    def getOutGoingTransitions(
        cls, discard=[], noskill=True, directions: list[DirectionsEnum] = [], mapIds=[]
    ) -> list[Transition]:
        result = []
        v = WorldPathFinder().getCurrentPlayerVertex()
        outgoingEdges = WorldPathFinder().worldGraph.getOutgoingEdgesFromVertex(v)
        for e in outgoingEdges:
            for tr in e.transitions:
                if tr.transitionMapId not in discard:
                    if noskill and tr.skillId > 0:
                        continue
                    if directions and (
                        tr.direction < 0
                        or DirectionsEnum(tr.direction) not in directions
                    ):
                        continue
                    if mapIds and tr.transitionMapId not in mapIds:
                        continue
                    result.append(tr)
        return result

    @classmethod
    def changeMapToDstDirection(
        cls, direction: DirectionsEnum, discard: list[int] = []
    ) -> None:
        transitions = cls.getOutGoingTransitions(
            discard=discard, directions=[direction]
        )
        if len(transitions) == 0:
            raise Exception(f"No transition found towards direction '{direction.name}'")
        cls.sendClickAdjacentMsg(transitions[0].transitionMapId, transitions[0].cell)

    @classmethod
    def changeMapToDstCoords(cls, x: int, y: int, discard: list[int] = []):
        transitions = cls.getOutGoingTransitions(discard)
        if len(transitions) == 0:
            raise Exception(f"No transition found towards coords '{x, y}'")
        for tr in transitions:
            mp = MapPosition.getMapPositionById(tr.transitionMapId)
            if mp.posX == x and mp.posY == y:
                cls.sendClickAdjacentMsg(tr.transitionMapId, tr.cell)
                return tr.transitionMapId
        return -1

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
    def changeMapToDstMapdId(cls, destMapId: int, discard=[]) -> None:
        transitions = cls.getOutGoingTransitions(discard=discard, mapIds=[destMapId])
        if len(transitions) == 0:
            raise Exception(f"No transition found towards mapId '{destMapId}'")
        cls.sendClickAdjacentMsg(transitions[0].transitionMapId, transitions[0].cell)
