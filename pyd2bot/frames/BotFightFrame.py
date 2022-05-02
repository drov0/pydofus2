import math
import random
from threading import Timer
from types import FunctionType
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.atouin.messages.CellClickMessage import CellClickMessage
from com.ankamagames.atouin.messages.MapLoadedMessage import MapLoadedMessage
from com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionType import ConnectionType
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)
from com.ankamagames.dofus.logic.game.fight.miscs.FightReachableCellsMaker import (
    FightReachableCellsMaker,
)
from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import (
    RoleplayEntitiesFrame,
)
from com.ankamagames.dofus.network.messages.common.basic.BasicPingMessage import (
    BasicPingMessage,
)
from com.ankamagames.dofus.network.messages.game.actions.fight.GameActionFightCastRequestMessage import (
    GameActionFightCastRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.actions.sequence.SequenceEndMessage import (
    SequenceEndMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightEndMessage import (
    GameFightEndMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightJoinMessage import (
    GameFightJoinMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightReadyMessage import (
    GameFightReadyMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightTurnFinishMessage import (
    GameFightTurnFinishMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightTurnStartMessage import (
    GameFightTurnStartMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.character.GameFightShowFighterMessage import (
    GameFightShowFighterMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightMonsterInformations import (
    GameFightMonsterInformations,
)
from com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayGroupMonsterInformations import (
    GameRolePlayGroupMonsterInformations,
)
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.entities.interfaces.IInteractive import IInteractive
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from com.ankamagames.jerakine.types.enums.Priority import Priority
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.fight.frames.FightTurnFrame import (
        FightTurnFrame,
    )
    from com.ankamagames.dofus.logic.game.fight.frames.FightContextFrame import (
        FightContextFrame,
    )

logger = Logger(__name__)


class BotFightFrame(Frame, metaclass=Singleton):

    _frameFightListRequest: bool

    _fightCount: int = 0

    _mapPos: list

    _enabled: bool

    _inFight: bool

    _lastEntityOver: IInteractive

    _wait: bool

    _turnPlayed: int

    _myTurn: bool

    _turnAction: list

    def __init__(self):
        self._turnAction = []
        super().__init__()

    def pushed(self) -> bool:
        self._enabled = True
        self.fakeActivity()
        self._myTurn = False
        self._mapPos = MapPosition.getMapPositions()
        return True

    def pulled(self) -> bool:
        self._enabled = False
        return True

    @property
    def priority(self) -> int:
        return Priority.LOW

    @property
    def fightCount(self) -> int:
        return self._fightCount

    def process(self, msg: Message) -> bool:

        if isinstance(msg, GameFightJoinMessage):
            self._fightCount += 1
            self._inFight = True
            return True

        if isinstance(msg, GameFightEndMessage):
            self._inFight = False
            return True

        if isinstance(msg, MapComplementaryInformationsDataMessage):
            self._wait = False
            return True

        if isinstance(msg, MapLoadedMessage):
            self._wait = True
            return True

        if isinstance(msg, GameFightShowFighterMessage):
            self._turnPlayed = 0
            self._myTurn = False
            startFightMsg = GameFightReadyMessage()
            startFightMsg.init(True)
            ConnectionsHandler.getConnection().send(startFightMsg)
            return True

        if isinstance(msg, GameFightTurnStartMessage):
            turnStartMsg = msg
            self._turnAction = []
            if turnStartMsg.id == PlayedCharacterManager().id:
                self._myTurn = True
                self._turnPlayed += 1
                self.addTurnAction(self.fightRandomMove, [])
                self.addTurnAction(self.turnEnd, [])
                self.nextTurnAction()
            else:
                self._myTurn = False
            return True

        if isinstance(msg, SequenceEndMessage):
            self.nextTurnAction()
            return True

        return False

    def nextTurnAction(self) -> None:
        action: object = None
        if len(self._turnAction) > 0:
            action = self._turnAction.pop(0)
            action["fct"](*action["args"])

    def addTurnAction(self, fct: FunctionType, args: list) -> None:
        self._turnAction.append({"fct": fct, "args": args})

    def turnEnd(self) -> None:
        finDeTourMsg: GameFightTurnFinishMessage = GameFightTurnFinishMessage()
        finDeTourMsg.init(False)
        ConnectionsHandler.getConnection().send(finDeTourMsg)

    def fakeActivity(self) -> None:
        if not self._enabled:
            return
        Timer(60 * 5, self.fakeActivity).start()
        bpmgs: BasicPingMessage = BasicPingMessage()
        bpmgs.init(False)
        ConnectionsHandler.getConnection().send(bpmgs, ConnectionType.TO_ALL_SERVERS)

    def randomWalk(self) -> None:
        entity = None
        groupEntity: IEntity = None
        if self._inFight or self._wait:
            return
        rpEF: "RoleplayEntitiesFrame" = (
            Kernel().getWorker().getFrame("RoleplayEntitiesFrame")
        )
        if not rpEF:
            return
        avaibleCells: list = []
        for entity in rpEF.entities:
            if isinstance(entity, GameRolePlayGroupMonsterInformations):
                groupEntity = DofusEntities.getEntity(
                    GameRolePlayGroupMonsterInformations(entity).contextualId
                )
                avaibleCells.append(MapPoint.fromCellId(groupEntity.position.cellId))
        if not avaibleCells or not len(avaibleCells):
            return
        ccmsg: CellClickMessage = CellClickMessage()
        ccmsg.cell = avaibleCells[math.floor(len(avaibleCells) * random.random())]
        ccmsg.cellId = ccmsg.cell.cellId
        ccmsg.id = MapDisplayManager().currentMapPoint.mapId
        Kernel().getWorker().process(ccmsg)

    def fightRandomMove(self) -> None:
        reachableCellsMaker: FightReachableCellsMaker = FightReachableCellsMaker(
            FightEntitiesFrame.getCurrentInstance().getEntityInfos(
                PlayedCharacterManager().id
            )
        )
        logger.debug(f"found {len(reachableCellsMaker.reachableCells)} reachable cells")
        if len(reachableCellsMaker.reachableCells) == 0:
            self.nextTurnAction()
            return
        randomCell: int = random.choice(reachableCellsMaker.reachableCells)
        self.moveToCell(MapPoint.fromCellId(randomCell))

    def castSpell(self, spellId: int, onMySelf: bool) -> None:
        cellId: int = 0
        avaibleCells: list = None
        entity = None
        monster: GameFightMonsterInformations = None
        gafcrmsg: GameActionFightCastRequestMessage = (
            GameActionFightCastRequestMessage()
        )
        if onMySelf:
            cellId = (
                FightEntitiesFrame.getCurrentInstance()
                .getEntityInfos(PlayedCharacterManager().id)
                .disposition.cellId
            )
        else:
            avaibleCells = []
            for entity in FightEntitiesFrame.getCurrentInstance().entities.values():
                if entity.contextualId < 0 and isinstance(
                    entity, GameFightMonsterInformations
                ):
                    monster = entity
                    if monster.spawnInfo.alive:
                        avaibleCells.append(entity.disposition.cellId)
            logger.debug(avaibleCells)
            cellId = avaibleCells[math.floor(len(avaibleCells) * random.random())]
        gafcrmsg.init(spellId, cellId)
        ConnectionsHandler.getConnection().send(gafcrmsg)

    def moveToCell(self, cell: MapPoint) -> None:
        if not self._myTurn:
            logger.debug("Wants to move when it's not its turn yet")
            return False
        fightTurnFrame: "FightTurnFrame" = (
            Kernel().getWorker().getFrame("FightTurnFrame")
        )
        if not fightTurnFrame:
            logger.debug(
                "Wants to move inside fight but 'FightTurnFrame' not found in kernel"
            )
            return False
        logger.debug(
            f"Current cell {fightTurnFrame._playerEntity.position.cellId} moving to cell {cell.cellId}"
        )
        fightTurnFrame.drawPath(cell)
        fightTurnFrame.askMoveTo(cell)
        return True
