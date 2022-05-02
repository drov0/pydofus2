from datetime import datetime
import math
from com.ankamagames.atouin.messages.CellClickMessage import CellClickMessage
from com.ankamagames.atouin.messages.EntityMovementCompleteMessage import (
    EntityMovementCompleteMessage,
)
from com.ankamagames.atouin.messages.MapContainerRollOutMessage import (
    MapContainerRollOutMessage,
)
from com.ankamagames.atouin.types.Selection import Selection
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from com.ankamagames.dofus.internalDatacenter.stats.EntityStats import EntityStats
from com.ankamagames.dofus.internalDatacenter.stats.Stat import Stat
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.common.managers.StatsManager import StatsManager
from com.ankamagames.dofus.logic.game.common.managers.MapMovementAdapter import (
    MapMovementAdapter,
)
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.actions.GameFightSpellCastAction import (
    GameFightSpellCastAction,
)
from com.ankamagames.dofus.logic.game.fight.actions.GameFightTurnFinishAction import (
    GameFightTurnFinishAction,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.fight.frames.FightContextFrame import (
        FightContextFrame,
    )
    from com.ankamagames.dofus.logic.game.fight.frames.FightSpellCastFrame import (
        FightSpellCastFrame,
    )
from com.ankamagames.dofus.logic.game.fight.managers.CurrentPlayedFighterManager import (
    CurrentPlayedFighterManager,
)
from com.ankamagames.dofus.logic.game.fight.miscs.FightReachableCellsMaker import (
    FightReachableCellsMaker,
)
from com.ankamagames.dofus.logic.game.fight.miscs.TackleUtil import TackleUtil
from com.ankamagames.dofus.network.enums.ChatActivableChannelsEnum import (
    ChatActivableChannelsEnum,
)
from com.ankamagames.dofus.network.messages.game.chat.ChatClientMultiMessage import (
    ChatClientMultiMessage,
)
from com.ankamagames.dofus.network.messages.game.context.GameMapMovementRequestMessage import (
    GameMapMovementRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.GameMapNoMovementMessage import (
    GameMapNoMovementMessage,
)
from com.ankamagames.dofus.network.messages.game.context.ShowCellRequestMessage import (
    ShowCellRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightTurnFinishMessage import (
    GameFightTurnFinishMessage,
)
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightTurnReadyRequestMessage import (
    GameFightTurnReadyRequestMessage,
)
from com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristicsInformations import (
    CharacterCharacteristicsInformations,
)
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import (
    GameFightFighterInformations,
)
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.data.XmlConfig import XmlConfig
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.pathfinding.Pathfinding import Pathfinding
from com.ankamagames.jerakine.types.enums.Priority import Priority
from com.ankamagames.jerakine.types.events.PropertyChangeEvent import (
    PropertyChangeEvent,
)
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from com.ankamagames.jerakine.types.positions.MovementPath import MovementPath
from com.ankamagames.jerakine.types.positions.PathElement import PathElement
from damageCalculation.tools.StatIds import StatIds
from threading import Timer
from typing import TYPE_CHECKING

from com.ankamagames.dofus.logic.game.fight.frames.FightEntitiesFrame import (
    FightEntitiesFrame,
)

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.fight.frames.FightBattleFrame import (
        FightBattleFrame,
    )
    from com.ankamagames.jerakine.entities.interfaces.IMovable import IMovable
logger = Logger(__name__)


class FightTurnFrame(Frame):

    TAKLED_CURSOR_NAME: str = "TackledCursor"

    SELECTION_PATH: str = "FightMovementPath"

    SELECTION_END_PATH: str = "FightMovementEndPath"

    SELECTION_PATH_TACKLED: str = "FightMovementPathTackled"

    SELECTION_PATH_UNREACHABLE: str = "FightMovementPathUnreachable"

    SELECTION_MOVEMENT_AREA: str = "FightMovementArea"

    REMIND_TURN_DELAY: int = 15

    _movementSelection: Selection = None

    _movementTargetSelection: Selection = None

    _movementSelectionTackled: Selection = None

    _movementSelectionUnreachable: Selection = None

    _movementAreaSelection: Selection = None

    _isRequestingMovement: bool = None

    _spellCastFrame: Frame = None

    _finishingTurn: bool = None

    _remindTurnTimeoutId: Timer = None

    _myTurn: bool = None

    _turnDuration: int = None

    _remainingDurationSeconds: int = None

    _lastCell: MapPoint = None

    _cells: list[int] = None

    _cellsTackled: list[int] = None

    _cellsUnreachable: list[int] = None

    _lastPath: MovementPath = None

    _intervalTurn: Timer = None

    _playerEntity: IEntity = None

    _currentFighterId: float = None

    _tackleByCellId: dict = None

    _turnFinishingNoNeedToRedrawMovement: bool = False

    _lastMP: int = 0

    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.HIGH

    @property
    def myTurn(self) -> bool:
        return self._myTurn

    @myTurn.setter
    def myTurn(self, b: bool) -> None:
        refreshTarget = b != self._myTurn
        monsterEndTurn = not self._myTurn
        self._finishingTurn = False
        self._currentFighterId = CurrentPlayedFighterManager().currentFighterId
        self._playerEntity = DofusEntities.getEntity(self._currentFighterId)
        self._turnFinishingNoNeedToRedrawMovement = False
        self._myTurn = b
        if b:
            self.startRemindTurn()
            self.drawMovementArea()
        else:
            self._isRequestingMovement = False
            if self._remindTurnTimeoutId is not None:
                self._remindTurnTimeoutId.cancel()
            self.removePath()
            self.removeMovementArea()
        fcf: "FightContextFrame" = Kernel().getWorker().getFrame("FightContextFrame")
        if fcf:
            fcf.refreshTimelineOverEntityInfos()
        scf: "FightSpellCastFrame" = Kernel().getWorker().getFrame("FightSpellCastFrame")
        if scf:
            if monsterEndTurn:
                scf.drawRange()
            if refreshTarget:
                if scf:
                    scf.refreshTarget(True)
        if self._myTurn and not scf:
            self.drawPath()
        else:
            logger.debug(f"FightTurnFrame: not my turn {self._myTurn} or inside spell cast frame {scf}")

    @property
    def turnDuration(self) -> int:
        return self._turnDuration

    @turnDuration.setter
    def turnDuration(self, v: int) -> None:
        self._turnDuration = v
        self._remainingDurationSeconds = math.floor(v)
        if self._intervalTurn:
            self._intervalTurn.cancel()
        self._intervalTurn = Timer(10, self.onSecondTick)

    @property
    def lastPath(self) -> MovementPath:
        return self._lastPath

    @property
    def movementAreaSelection(self) -> Selection:
        return self._movementAreaSelection

    def freePlayer(self) -> None:
        self._isRequestingMovement = False

    def pushed(self) -> bool:
        StatsManager().addListenerToStat(StatIds.MOVEMENT_POINTS, self.onUpdateMovementPoints)
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, GameFightSpellCastAction):
            gfsca = msg
            if self._spellCastFrame is not None:
                Kernel().getWorker().removeFrame(self._spellCastFrame)
            self.removePath()
            if self._myTurn:
                self.startRemindTurn()
            bf: "FightBattleFrame" = Kernel().getWorker().getFrame("FightBattleFrame")
            playerInformation: "GameFightFighterInformations" = FightEntitiesFrame.getCurrentInstance().getEntityInfos(
                self._currentFighterId
            )
            if bf and bf.turnsCount <= 1 or playerInformation and playerInformation.spawnInfo.alive:
                import com.ankamagames.dofus.logic.game.fight.frames.FightSpellCastFrame as fscf

                self._spellCastFrame = fscf.FightSpellCastFrame(gfsca.spellId)
                Kernel().getWorker().addFrame(self._spellCastFrame)
            return True

        elif isinstance(msg, CellClickMessage):
            ccmsg = msg
            if not self.myTurn:
                return False
            self.askMoveTo(ccmsg.cell)
            return True

        elif isinstance(msg, GameMapNoMovementMessage):
            if not self.myTurn:
                return False
            self._isRequestingMovement = False
            self.removePath()
            return True

        elif isinstance(msg, EntityMovementCompleteMessage):
            emcmsg = msg
            fcf: "FightContextFrame" = Kernel().getWorker().getFrame("FightContextFrame")
            fcf.refreshTimelineOverEntityInfos()
            if not self.myTurn:
                return True
            if emcmsg.entity.id == self._currentFighterId:
                self._isRequestingMovement = False
                spellCastFrame: "FightSpellCastFrame" = Kernel().getWorker().getFrame("FightSpellCastFrame")
                if not spellCastFrame:
                    self.drawPath()
                self.startRemindTurn()
                if self._finishingTurn:
                    self.finishTurn()
            return True

        if isinstance(msg, GameFightTurnFinishAction):
            if not self.myTurn:
                return False
            self._turnFinishingNoNeedToRedrawMovement = True
            entitiesFrame: "FightEntitiesFrame" = Kernel().getWorker().getFrame("FightEntitiesFrame")
            playerInfos: "GameFightFighterInformations" = entitiesFrame.getEntityInfos(self._currentFighterId)
            if self._remainingDurationSeconds > 0 and not playerInfos.stats.summoned:
                basicTurnDuration = CurrentPlayedFighterManager().getBasicTurnDuration()
                secondsToReport = math.floor(self._remainingDurationSeconds / 2)
                if basicTurnDuration + secondsToReport > 60:
                    secondsToReport = 60 - basicTurnDuration
                if secondsToReport > 0:
                    Logger.debug(
                        I18n.getUiText("ui.fight.secondsAdded", [secondsToReport]),
                        "n",
                        secondsToReport <= 1,
                        secondsToReport == 0,
                    )
                self._remainingDurationSeconds = 0
                self._intervalTurn = 0
            imE: "IMovable" = DofusEntities.getEntity(self._currentFighterId)
            if not imE:
                return True
            if imE.isMoving:
                self._finishingTurn = True
            else:
                self.finishTurn()
            return True

        if isinstance(msg, MapContainerRollOutMessage):
            self.removePath()
            return True

        if isinstance(msg, GameFightTurnReadyRequestMessage):
            self._turnFinishingNoNeedToRedrawMovement = True
            return False
        else:
            return False

    def pulled(self) -> bool:
        StatsManager().removeListenerFromStat(StatIds.MOVEMENT_POINTS, self.onUpdateMovementPoints)
        if self._remindTurnTimeoutId:
            self._remindTurnTimeoutId.cancel()
        if self._intervalTurn:
            self._intervalTurn.cancel()
        self.removePath()
        self.removeMovementArea()
        Kernel().getWorker().removeFrame(self._spellCastFrame)
        return True

    def drawMovementArea(self) -> list[int]:
        logger.debug("drawing the movement area")
        if not self._playerEntity or self._playerEntity.isMoving:
            logger.debug(f"player {self._playerEntity} is moving {self._playerEntity.isMoving} or not found")
            self.removeMovementArea()
            return []
        playerPosition: MapPoint = self._playerEntity.position
        stats: EntityStats = CurrentPlayedFighterManager().getStats()
        if not stats:
            logger.debug("no stats")
            return
        movementPoints: int = stats.getStatTotalValue(StatIds.MOVEMENT_POINTS)
        logger.debug(f"movementPoints available {movementPoints}")
        self._lastMP = movementPoints
        entitiesFrame: FightEntitiesFrame = FightEntitiesFrame.getCurrentInstance()
        playerInfos: GameFightFighterInformations = entitiesFrame.getEntityInfos(self._playerEntity.id)
        tackle: float = TackleUtil.getTackle(playerInfos, playerPosition)
        logger.debug(f"tackle computed {tackle}")
        self._tackleByCellId = dict()
        self._tackleByCellId[playerPosition.cellId] = tackle
        mpLost: int = int(movementPoints * (1 - tackle) + 0.5)
        logger.debug(f"mpLost {mpLost}")
        if mpLost < 0:
            mpLost = 0
        movementPoints -= mpLost
        if movementPoints == 0:
            self.removeMovementArea()
            return []
        fightReachableCellsMaker: FightReachableCellsMaker = FightReachableCellsMaker(playerInfos)
        reachableCells: list[int] = fightReachableCellsMaker.reachableCells
        if len(reachableCells) == 0:
            self.removeMovementArea()
            return []
        return reachableCells

    def drawPath(self, destCell: MapPoint = None) -> None:
        firstObstacle: PathElement = None
        if self._cells is None:
            self._cells = []
        logger.debug("drawing the move path")
        if Kernel().getWorker().contains("FightSpellCastFrame"):
            return
        fcf: "FightContextFrame" = Kernel().getWorker().getFrame("FightContextFrame")
        if self._isRequestingMovement:
            logger.debug("requesting movement")
            return
        if not destCell:
            if fcf.currentCell == -1:
                logger.debug("no destination cell")
                return
            destCell = MapPoint.fromCellId(fcf.currentCell)
        if not self._playerEntity:
            logger.debug("no player entity")
            self.removePath()
            return
        stats: EntityStats = CurrentPlayedFighterManager().getStats()
        mpLost: int = 0
        apLost: int = 0
        movementPoints: int = stats.getStatTotalValue(StatIds.MOVEMENT_POINTS)
        actionPoints: int = stats.getStatTotalValue(StatIds.ACTION_POINTS)
        logger.debug(f"MP : {movementPoints}, AP : {actionPoints}")
        if self._playerEntity.isMoving or self._playerEntity.position.distanceToCell(destCell) > movementPoints:
            logger.debug("player is moving or dest is too far")
            self.removePath()
            return
        path: MovementPath = Pathfinding.findPath(
            DataMapProvider(), self._playerEntity.position, destCell, False, False, True
        )
        logger.debug(
            f"path found of length {len(path.path)}, having {len(DataMapProvider().obstaclesCells)} obstacles"
        )
        if len(DataMapProvider().obstaclesCells) > 0 and (len(path.path) == 0 or len(path.path) > movementPoints):
            path = Pathfinding.findPath(
                DataMapProvider(),
                self._playerEntity.position,
                destCell,
                False,
                False,
                False,
            )
            logger.debug(
                f"path found of length {len(path.path)}, having {len(DataMapProvider().obstaclesCells)} obstacles"
            )
            if len(path.path) > 0:
                pathLen = len(path.path)
                for i in range(pathLen):
                    if path.path[i].cellId in DataMapProvider().obstaclesCells:
                        firstObstacle = path.path[i]
                        for j in range(pathLen):
                            self._cellsUnreachable.append(path.path[j].cellId)
                        self._cellsUnreachable.append(path.end.cellId)
                        path.end = firstObstacle.step
                        path.path = path.path[:i]
                        break
        if len(path.path) == 0 or len(path.path) > movementPoints:
            logger.debug(f"Path found empty {len(path.path)} or too long compared to mp {movementPoints}")
            self.removePath()
            return
        self._lastPath = path
        isFirst: bool = True
        mpCount: int = 0
        apLost = 0
        lastPe: PathElement = None
        entitiesFrame: "FightEntitiesFrame" = Kernel().getWorker().getFrame("FightEntitiesFrame")
        playerInfos: GameFightFighterInformations = entitiesFrame.getEntityInfos(self._playerEntity.id)
        for pe in path.path:
            if isFirst:
                isFirst = False
            else:
                tackle = TackleUtil.getTackle(playerInfos, lastPe.step)
                mpLost += int((movementPoints - mpCount) * (1 - tackle) + 0.5)
                if mpLost < 0:
                    mpLost = 0
                apLost += int(actionPoints * (1 - tackle) + 0.5)
                if apLost < 0:
                    apLost = 0
                movementPoints = stats.getStatTotalValue(StatIds.MOVEMENT_POINTS) - mpLost
                actionPoints = stats.getStatTotalValue(StatIds.ACTION_POINTS) - apLost
                if mpCount < movementPoints:
                    if mpLost > 0:
                        self._cellsTackled.append(pe.step.cellId)
                    else:
                        self._cells.append(pe.step.cellId)
                    mpCount += 1
                else:
                    self._cellsUnreachable.append(pe.step.cellId)
            lastPe = pe
        logger.debug(
            f"cells : {self._cells}, cellsTackled : {self._cellsTackled}, cellsUnreachable : {self._cellsUnreachable}"
        )
        tackle = TackleUtil.getTackle(playerInfos, lastPe.step)
        mpLost += int((movementPoints - mpCount) * (1 - tackle) + 0.5)
        if mpLost < 0:
            mpLost = 0
        apLost += int(actionPoints * (1 - tackle) + 0.5)
        if apLost < 0:
            apLost = 0
        movementPoints = stats.getStatTotalValue(StatIds.MOVEMENT_POINTS) - mpLost
        if mpCount < movementPoints:
            if firstObstacle:
                movementPoints = len(path.path)
            if mpLost > 0:
                self._cellsTackled.append(path.end.cellId)
            else:
                self._cells.append(path.end.cellId)
        elif firstObstacle:
            self._cellsUnreachable.insert(0, path.end.cellId)
            movementPoints = len(path.path) - 1
        else:
            self._cellsUnreachable.append(path.end.cellId)

        mp: MapPoint = MapPoint()
        mp.cellId = (
            int(self._cells[len(self._cells) - 2]) if len(self._cells) > 1 else int(playerInfos.disposition.cellId)
        )

    def updatePath(self) -> None:
        self.drawPath(self._lastCell)

    def removePath(self) -> None:
        self._movementSelection = None
        self._movementSelectionTackled = None
        self._movementSelectionUnreachable = None
        self._movementTargetSelection = None
        self._lastPath = None
        self._cells = None

    def removeMovementArea(self) -> None:
        self._movementAreaSelection = None

    def askMoveTo(self, cell: MapPoint) -> bool:
        if self._isRequestingMovement:
            logger.warn("Already requesting movement")
            return False
        self._isRequestingMovement = True
        if not self._playerEntity:
            logger.warn("The player tried to move before its character was added to the scene. Aborting.")
            self._isRequestingMovement = False
            return False
        if self._playerEntity.isMoving:
            logger.warn("The player is already moving")
            self._isRequestingMovement = False
            return False
        if (self._cells is None or len(self._cells) == 0) and (
            self._cellsTackled is None or len(self._cellsTackled) == 0
        ):
            logger.debug(f"No cells to move to {self._cells} {self._cellsTackled}")
            self._isRequestingMovement = False
            return False
        path: MovementPath = MovementPath()
        cells: list[int] = self._cells if (self._cells and len(self._cells)) else self._cellsTackled
        cells.insert(0, self._playerEntity.position.cellId)
        path.fillFromCellIds(cells[0 : len(cells) - 1])
        path.start = self._playerEntity.position
        path.end = MapPoint.fromCellId(cells[len(cells) - 1])
        path.path[len(path.path) - 1].orientation = path.path[len(path.path) - 1].step.orientationTo(path.end)
        fightBattleFrame: "FightBattleFrame" = Kernel().getWorker().getFrame("FightBattleFrame")
        if not fightBattleFrame or not fightBattleFrame.fightIsPaused:
            gmmrmsg = GameMapMovementRequestMessage()
            gmmrmsg.init(
                MapMovementAdapter.getServerMovement(path),
                PlayedCharacterManager().currentMap.mapId,
            )
            ConnectionsHandler.getConnection().send(gmmrmsg)
        else:
            self._isRequestingMovement = False
        self.removePath()
        return True

    def finishTurn(self) -> None:
        gftfmsg: GameFightTurnFinishMessage = GameFightTurnFinishMessage()
        gftfmsg.init(False)
        ConnectionsHandler.getConnection().send(gftfmsg)
        self.removeMovementArea()
        self._finishingTurn = False

    def startRemindTurn(self) -> None:
        if not self._myTurn:
            return
        # if self._turnDuration > 0 and Dofus().options.getOption("remindTurn"):
        #     if self._remindTurnTimeoutId is not None:
        #         self._remindTurnTimeoutId.cancel()
        #     self._remindTurnTimeoutId = Timer(self.REMIND_TURN_DELAY, self.remindTurn)
        #     self._remindTurnTimeoutId.start()

    def remindTurn(self) -> None:
        fightBattleFrame: "FightBattleFrame" = Kernel().getWorker().getFrame("FightBattleFrame")
        if fightBattleFrame and fightBattleFrame.fightIsPaused:
            self._remindTurnTimeoutId.cancel()
            self._remindTurnTimeoutId = None
            return
        self._remindTurnTimeoutId = None

    def onSecondTick(self) -> None:
        if self._remainingDurationSeconds > 0:
            self._remainingDurationSeconds -= 1
        else:
            self._intervalTurn.cancel()

    def onUpdateMovementPoints(self, stat: Stat) -> None:
        if stat and stat.entityId == self._currentFighterId and stat.totalValue is not self._lastMP:
            self.drawMovementArea()

    def showCell(self, cellId: MapPoint) -> None:
        if not Kernel().getWorker().contains("FightSpellCastFrame"):
            if DataMapProvider().pointMov(
                MapPoint.fromCellId(cellId).x,
                MapPoint.fromCellId(cellId).y,
                True,
            ):
                scrmsg = ShowCellRequestMessage()
                scrmsg.init(cellId)
                ConnectionsHandler.getConnection().send(scrmsg)
                text = I18n.getUiText(
                    "ui.fightAutomsg.cell",
                    ["{cell," + str(cellId) + "::" + str(cellId) + "}"],
                )
                ccmmsg = ChatClientMultiMessage()
                ccmmsg.init(content_=text, channel_=ChatActivableChannelsEnum.CHANNEL_TEAM)
                ConnectionsHandler.getConnection().send(ccmmsg)
