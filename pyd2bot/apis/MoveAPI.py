import random
from threading import Timer
from typing import TYPE_CHECKING
from com.ankamagames.dofus.datacenter.items.criterion.CriterionUtils import CriterionUtils
from com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import InteractiveElementData
from com.ankamagames.dofus.modules.utils.pathFinding.world.Edge import Edge

from com.ankamagames.dofus.modules.utils.pathFinding.world.Transition import Transition
from com.ankamagames.dofus.modules.utils.pathFinding.world.TransitionTypeEnum import TransitionTypeEnum

from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import (
    WorldPathFinder,
)
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint

if TYPE_CHECKING:
    from com.ankamagames.atouin.data.map.Map import Map
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame import (
        RoleplayInteractivesFrame,
    )
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame

import com.ankamagames.atouin.managers.MapDisplayManager as mdm
from com.ankamagames.atouin.messages.AdjacentMapClickMessage import (
    AdjacentMapClickMessage,
)
from com.ankamagames.atouin.messages.CellClickMessage import CellClickMessage
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.types.enums.DirectionsEnum import DirectionsEnum

logger = Logger("Dofus2")


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
                raise Exception(f"[MouvementAPI] InteractiveElement {randTransition.id} not found")
            logger.debug(
                f"[MouvementAPI] Activating skill {randTransition.skillId} to change map towards '{randTransition.transitionMapId}'"
            )
            rplInteractivesFrame.skillClicked(ie)
        else:
            logger.debug(
                f"[MouvementAPI] Sending a click to change map towards direction '{randTransition.transitionMapId}'"
            )
            cls.sendClickAdjacentMsg(randTransition.transitionMapId, randTransition.cell)
        return randTransition.transitionMapId, randTransition.skillId

    @classmethod
    def getOutGoingTransitions(
        cls, discard=[], noskill=True, directions: list[DirectionsEnum] = [], mapIds=[]
    ) -> list[Transition]:
        result = []
        v = WorldPathFinder().currPlayerVertex
        logger.debug(f"current map {v.mapId}")
        outgoingEdges = WorldPathFinder().worldGraph.getOutgoingEdgesFromVertex(v)
        for e in outgoingEdges:
            if e.dst.mapId in discard:
                continue
            for tr in e.transitions:
                if noskill and tr.skillId > 0:
                    continue
                if directions and (tr.direction < 0 or DirectionsEnum(tr.direction) not in directions):
                    continue
                if mapIds and tr.transitionMapId not in mapIds:
                    continue
                result.append(tr)
        return result

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

    @classmethod
    def followEdge(cls, edge: Edge):
        for tr in edge.transitions:
            if tr.isValid:
                cls.followTransition(tr)
                return True
        raise Exception("No valid transition found!!!")

    @classmethod
    def getTransitionIe(cls, transition: Transition) -> "InteractiveElementData":
        rpframe: "RoleplayInteractivesFrame" = Kernel().getWorker().getFrame("RoleplayInteractivesFrame")
        ie = rpframe.getInteractiveElement(transition.id, transition.skillId)
        return ie

    @classmethod
    def followTransition(cls, tr: Transition):
        if not tr.isValid:
            raise Exception("Trying to follow a NON valid transition")
        if TransitionTypeEnum(tr.type) == TransitionTypeEnum.INTERACTIVE:
            logger.debug(f"Activating skill {tr.skillId} to change map towards '{tr.transitionMapId}'")
            ie = cls.getTransitionIe(tr)
            rpmframe: "RoleplayMovementFrame" = Kernel().getWorker().getFrame("RoleplayMovementFrame")
            if tr.cell != PlayedCharacterManager().entity.position.cellId:
                rpmframe.setFollowingInteraction(
                    {
                        "ie": ie.element,
                        "skillInstanceId": ie.skillUID,
                        "additionalParam": 0,
                    }
                )
                rpmframe.resetNextMoveMapChange()
                rpmframe.askMoveTo(ie.position)
            else:
                rpmframe.activateSkill(ie.skillUID, tr.id, 0)
        else:
            logger.debug(f"Classic map change map towards '{tr.transitionMapId}'")
            cls.sendClickAdjacentMsg(tr.transitionMapId, tr.cell)

    @classmethod
    def neighborMapIdFromcoords(cls, x: int, y: int) -> int:
        v = WorldPathFinder().currPlayerVertex
        if not v:
            Timer(0.1, cls.neighborMapIdFromcoords, [x, y]).start()
            return
        outgoingEdges = WorldPathFinder().worldGraph.getOutgoingEdgesFromVertex(v)
        for edge in outgoingEdges:
            mp = MapPosition.getMapPositionById(edge.dst.mapId)
            if mp.posX == x and mp.posY == y:
                for tr in edge.transitions:
                    if tr.isValid:
                        return tr.transitionMapId

    @classmethod
    def changeMapToDstCoords(cls, x: int, y: int) -> None:
        v = WorldPathFinder().currPlayerVertex
        outgoingEdges = WorldPathFinder().worldGraph.getOutgoingEdgesFromVertex(v)
        for edge in outgoingEdges:
            mp = MapPosition.getMapPositionById(edge.dst.mapId)
            if mp.posX == x and mp.posY == y:
                for tr in edge.transitions:
                    if tr.isValid:
                        cls.followTransition(tr)
                        return True
