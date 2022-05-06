from threading import Timer
from time import perf_counter, sleep
from com.ankamagames.atouin.managers.EntitiesManager import EntitiesManager
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.atouin.messages.EntityMovementCompleteMessage import (
    EntityMovementCompleteMessage,
)
from com.ankamagames.atouin.messages.EntityMovementStoppedMessage import (
    EntityMovementStoppedMessage,
)
from com.ankamagames.atouin.utils.DataMapProvider import DataMapProvider
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.MapMovementAdapter import (
    MapMovementAdapter,
)
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.common.misc.DofusEntities import DofusEntities
from com.ankamagames.dofus.logic.game.fight.messages.MapMoveFailed import MapMoveFailed
from com.ankamagames.dofus.logic.game.fight.messages.FightRequestFailed import FightRequestFailed
from com.ankamagames.dofus.logic.game.roleplay.actions.PlayerFightRequestAction import (
    PlayerFightRequestAction,
)
import com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame as rif

from com.ankamagames.dofus.logic.game.roleplay.messages.CharacterMovementStoppedMessage import (
    CharacterMovementStoppedMessage,
)
from com.ankamagames.dofus.network.enums.PlayerLifeStatusEnum import (
    PlayerLifeStatusEnum,
)
from com.ankamagames.dofus.network.messages.game.context.GameMapMovementCancelMessage import (
    GameMapMovementCancelMessage,
)
from com.ankamagames.dofus.network.messages.game.context.GameMapMovementConfirmMessage import (
    GameMapMovementConfirmMessage,
)
from com.ankamagames.dofus.network.messages.game.context.GameMapMovementMessage import (
    GameMapMovementMessage,
)
from com.ankamagames.dofus.network.messages.game.context.GameMapMovementRequestMessage import (
    GameMapMovementRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.GameMapNoMovementMessage import (
    GameMapNoMovementMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.ChangeMapMessage import (
    ChangeMapMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.CurrentMapMessage import (
    CurrentMapMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapChangeFailedMessage import (
    MapChangeFailedMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.TeleportOnSameMapMessage import (
    TeleportOnSameMapMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.delay.GameRolePlayDelayedActionFinishedMessage import (
    GameRolePlayDelayedActionFinishedMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.fight.GameRolePlayAttackMonsterRequestMessage import (
    GameRolePlayAttackMonsterRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.fight.GameRolePlayFightRequestCanceledMessage import (
    GameRolePlayFightRequestCanceledMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.havenbag.EditHavenBagFinishedMessage import (
    EditHavenBagFinishedMessage,
)
from com.ankamagames.dofus.network.messages.game.dialog.LeaveDialogMessage import (
    LeaveDialogMessage,
)
from com.ankamagames.dofus.network.messages.game.guild.tax.GuildFightPlayersHelpersLeaveMessage import (
    GuildFightPlayersHelpersLeaveMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseEndedMessage import (
    InteractiveUseEndedMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseErrorMessage import (
    InteractiveUseErrorMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseRequestMessage import (
    InteractiveUseRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUsedMessage import (
    InteractiveUsedMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.skill.InteractiveUseWithParamRequestMessage import (
    InteractiveUseWithParamRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeLeaveMessage import (
    ExchangeLeaveMessage,
)
from com.ankamagames.dofus.network.messages.game.prism.PrismFightDefenderLeaveMessage import (
    PrismFightDefenderLeaveMessage,
)
from com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayGroupMonsterInformations import (
    GameRolePlayGroupMonsterInformations,
)
from com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayGroupMonsterWaveInformations import (
    GameRolePlayGroupMonsterWaveInformations,
)
from com.ankamagames.dofus.network.types.game.interactive.InteractiveElement import (
    InteractiveElement,
)
from com.ankamagames.dofus.types.entities.AnimatedCharacter import AnimatedCharacter
from com.ankamagames.jerakine.entities.interfaces.IEntity import IEntity
from com.ankamagames.jerakine.entities.interfaces.IMovable import IMovable
from com.ankamagames.jerakine.handlers.messages.Action import Action
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.network.INetworkMessage import INetworkMessage
from com.ankamagames.jerakine.pathfinding.Pathfinding import Pathfinding
from com.ankamagames.jerakine.types.enums.Priority import Priority
from com.ankamagames.jerakine.types.positions.MapPoint import MapPoint
from com.ankamagames.jerakine.types.positions.MovementPath import MovementPath
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import RoleplayEntitiesFrame

logger = Logger("Dofus2")


class RoleplayMovementFrame(Frame):
    CONSECUTIVE_MOVEMENT_DELAY: int = 0.25
    VERBOSE = True

    _wantToChangeMap: float = -1

    _changeMapByAutoTrip: bool = False

    _followingMove: MapPoint

    _followingIe: object

    _followingMonsterGroup: GameRolePlayGroupMonsterInformations

    _followingMessage = None

    _isRequestingMovement: bool

    _latestMovementRequest: int

    _destinationPoint: int

    _nextMovementBehavior: int

    _lastPlayerValidatedPosition: MapPoint

    _lastMoveEndCellId: int

    _canMove: bool = True

    _mapHasAggressiveMonsters: bool = False

    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.NORMAL

    @property
    def isRequestingMovement(self) -> bool:
        return self._isRequestingMovement

    @property
    def entitiesFrame(self) -> "RoleplayEntitiesFrame":
        return Kernel().getWorker().getFrame("RoleplayEntitiesFrame")

    def pushed(self) -> bool:
        self._wantToChangeMap = -1
        self._changeMapByAutoTrip = False
        self._followingIe = None
        self._followingMonsterGroup = None
        self._followingMove = None
        self._isRequestingMovement = False
        self._latestMovementRequest = 0
        self._lastMoveEndCellId = None
        self._changeMapTimeout = None
        self._changeMapFails = 0
        self._requestFightTimeout = None
        self._requestFighFails = 0
        self._moveRequetFails = 0
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, GameMapNoMovementMessage):
            logger.debug("Movement impossible")
            if self._moveRequetFails > 0:
                Kernel().getWorker().process(MapMoveFailed())
            self._moveRequetFails += 1
            if self._changeMapTimeout:
                self._changeMapTimeout.cancel()
            self._canMove = True
            self._isRequestingMovement = False

            if self._followingIe:
                self.activateSkill(
                    self._followingIe["skillInstanceId"],
                    self._followingIe["ie"],
                    self._followingIe["additionalParam"],
                )
                self._followingIe = None

            if self._followingMonsterGroup:
                self.requestMonsterFight(self._followingMonsterGroup.contextualId)
                self._followingMonsterGroup = None

            else:
                gmnmm = msg
                newPos = MapPoint.fromCoords(gmnmm.cellX, gmnmm.cellY)
                player: AnimatedCharacter = DofusEntities.getEntity(PlayedCharacterManager().id)
                if not player:
                    return True
                if player.isMoving:
                    player.stop = True
                player.position = newPos
                if not PlayedCharacterManager().isFighting and self._wantToChangeMap:
                    mp = MapPoint.fromCellId(self._destinationPoint)
                    if newPos == mp:
                        self.askMapChange()
                    else:
                        self.askMoveTo(mp)
            return True

        if isinstance(msg, GameMapMovementMessage):
            gmmmsg = msg
            movedEntity = DofusEntities.getEntity(gmmmsg.actorId)
            # logger.debug(f"[MapMovement] Movement of actor {gmmmsg.actorId}")
            clientMovePath = MapMovementAdapter.getClientMovement(gmmmsg.keyMovements)
            if movedEntity:
                logger.info(
                    f"[MapMovement] Entity {movedEntity.id} moved from {movedEntity.position.cellId} to {clientMovePath.end.cellId}"
                )
                movedEntity.position.cellId = clientMovePath.end.cellId
                self.entitiesFrame.updateEntityCellId(gmmmsg.actorId, clientMovePath.end.cellId)
            else:
                logger.warning(f"[MapMovement] Entity {gmmmsg.actorId} not found")

            if float(gmmmsg.actorId) != float(PlayedCharacterManager().id):
                self.applyGameMapMovement(float(gmmmsg.actorId), clientMovePath, msg)
                ne = self.entitiesFrame.getEntityInfos(gmmmsg.actorId)
                if ne and ne.disposition.cellId != clientMovePath.end.cellId:
                    raise Exception("Entity position not updated")

            else:
                self._isRequestingMovement = False
                pathDuration = max(1, clientMovePath.getCrossingDuration())
                sleep(pathDuration)
                Kernel().getWorker().processImmediately(EntityMovementCompleteMessage(movedEntity)),
            return True

        elif isinstance(msg, EntityMovementCompleteMessage):
            emcmsg = msg
            if emcmsg.entity.id == PlayedCharacterManager().id:
                logger.debug(
                    f"[RolePlayMovement] Mouvement complete, arrived at {emcmsg.entity.position.cellId}, destination point {self._destinationPoint}"
                )
                logger.debug(f"[RolePlayMovement] Wants to atack monsters? {self._followingMonsterGroup}")
                logger.debug(f"[RolePlayMovement] Wants to changemap monsters? {self._wantToChangeMap}")
                gmmcmsg = GameMapMovementConfirmMessage()
                ConnectionsHandler.getConnection().send(gmmcmsg)
                if self._wantToChangeMap and self._wantToChangeMap != -1:
                    logger.debug(f"[RolePlayMovement] Wants to change map to {self._wantToChangeMap}")
                    self._isRequestingMovement = False
                    if emcmsg.entity.position.cellId != self._destinationPoint:
                        logger.debug(
                            f"Wants to change map but didn't reach the map change cell will retry to reach it"
                        )
                        self.askMoveTo(MapPoint.fromCellId(self._destinationPoint))
                    else:
                        self.askMapChange()

                elif self._followingIe:
                    logger.debug(f"[RolePlayMovement] Wants to activate element {self._followingIe['ie'].elementId}")
                    self._isRequestingMovement = False
                    self.activateSkill(
                        self._followingIe["skillInstanceId"],
                        self._followingIe["ie"],
                        self._followingIe["additionalParam"],
                    )
                    self._followingIe = None

                elif self._followingMonsterGroup:
                    self._isRequestingMovement = False
                    self._followingMonsterGroup = self.entitiesFrame.getEntityInfos(
                        int(self._followingMonsterGroup.contextualId)
                    )
                    freshMonstersPosition = self._followingMonsterGroup.disposition
                    if freshMonstersPosition.cellId == emcmsg.entity.position.cellId:
                        self.requestMonsterFight(self._followingMonsterGroup.contextualId)
                        self._followingMonsterGroup = None
                    else:
                        self.askMoveTo(MapPoint.fromCellId(self._followingMonsterGroup.disposition.cellId))
                        self.requestMonsterFight(self._followingMonsterGroup.contextualId)
                Kernel().getWorker().processImmediately(CharacterMovementStoppedMessage())
            return True

        elif isinstance(msg, EntityMovementStoppedMessage):
            emsmsg = msg
            if emsmsg.entity.id == PlayedCharacterManager().id:
                canceledMoveMessage = GameMapMovementCancelMessage()
                canceledMoveMessage.init(emsmsg.entity.position.cellId)
                ConnectionsHandler.getConnection().send(canceledMoveMessage)
                self._isRequestingMovement = False
                if self._followingMove and self._canMove:
                    self.askMoveTo(self._followingMove)
                    self._followingMove = None
                if self._followingMessage:
                    if isinstance(self._followingMessage, PlayerFightRequestAction):
                        Kernel().getWorker().process(self._followingMessage)
                    else:
                        ConnectionsHandler.getConnection().send(self._followingMessage)
                    self._followingMessage = None
            return True

        elif isinstance(msg, TeleportOnSameMapMessage):
            tosmmsg = msg
            teleportedEntity = DofusEntities.getEntity(tosmmsg.targetId)
            if teleportedEntity:
                if isinstance(teleportedEntity, IMovable):
                    if teleportedEntity.isMoving:
                        teleportedEntity.stop(True)
                    teleportedEntity
                else:
                    logger.warn("Cannot teleport a non IMovable entity. WTF ?")
            else:
                logger.warn("Received a teleportation request for a non-existing entity. Aborting.")
            return True

        elif isinstance(msg, InteractiveUsedMessage):
            if msg.entityId == PlayedCharacterManager().id:
                self._canMove = msg.canMove
            return False

        elif isinstance(msg, InteractiveUseEndedMessage):
            self._canMove = True
            return False

        elif isinstance(msg, InteractiveUseErrorMessage):
            self._canMove = True
            return False

        elif isinstance(msg, LeaveDialogMessage):
            self._canMove = True
            return False

        elif isinstance(msg, ExchangeLeaveMessage):
            self._canMove = True
            return False

        elif isinstance(msg, EditHavenBagFinishedMessage):
            self._canMove = True
            return False

        elif isinstance(msg, GameRolePlayDelayedActionFinishedMessage):
            if msg.delayedCharacterId == PlayedCharacterManager().id:
                self._canMove = True
            return False

        elif isinstance(msg, GuildFightPlayersHelpersLeaveMessage):
            if msg.playerId == PlayedCharacterManager().id:
                self._canMove = True
            return False

        elif isinstance(msg, PrismFightDefenderLeaveMessage):
            if msg.fighterToRemoveId == PlayedCharacterManager().id:
                self._canMove = True
            return False

        elif isinstance(msg, GameRolePlayFightRequestCanceledMessage):
            if msg.targetId == PlayedCharacterManager().id or msg.sourceId == PlayedCharacterManager().id:
                self._canMove = True
            return False

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            self._mapHasAggressiveMonsters = msg.hasAggressiveMonsters
            self._isRequestingMovement = False
            return False

        else:
            return False

    def pulled(self) -> bool:
        return True

    def setNextMoveMapChange(self, mapId: float, autoTrip: bool = False) -> None:
        self._wantToChangeMap = mapId
        self._changeMapByAutoTrip = autoTrip

    def resetNextMoveMapChange(self) -> None:
        self._wantToChangeMap = -1
        self._changeMapByAutoTrip = False

    def setFollowingInteraction(self, interaction: object) -> None:
        self._followingIe = interaction

    def setFollowingMonsterFight(self, monsterGroup: object) -> None:
        self._followingMonsterGroup = monsterGroup

    def setFollowingMessage(self, message) -> None:
        if not isinstance(message, (INetworkMessage, Action)):
            raise Exception("The message is neither INetworkMessage or Action")
        self._followingMessage = message

    def forceNextMovementBehavior(self, pValue: int) -> None:
        self._nextMovementBehavior = pValue

    def askMoveTo(self, cell: MapPoint) -> bool:
        playerEntity: AnimatedCharacter = DofusEntities.getEntity(PlayedCharacterManager().id)
        if playerEntity.position.cellId == cell.cellId:
            logger.debug("[RolePlayMovement] Already on the cell")
        logger.debug(
            f"[RolePlayMovement] Asking move from cell {playerEntity.position.cellId} to cell {cell}, can Move {self._canMove}"
        )
        if not self._canMove or PlayedCharacterManager().state == PlayerLifeStatusEnum.STATUS_TOMBSTONE:
            logger.debug("[RolePlayMovement] Can't move or dead, aborting")
            return False
        if self._isRequestingMovement:
            logger.error("[RolePlayMovement] Already requesting movement, aborting", exc_info=True)
            return False
        now: int = perf_counter()
        nexPossibleMovementTime = self._latestMovementRequest + self.CONSECUTIVE_MOVEMENT_DELAY
        if now < nexPossibleMovementTime:
            sleep(self.CONSECUTIVE_MOVEMENT_DELAY)
        self._isRequestingMovement = True
        if playerEntity is None:
            logger.warn(
                "[RolePlayMovement] The player tried to move before its character was added to the scene. Aborting."
            )
            self._isRequestingMovement = False
            return False
        self._destinationPoint = cell.cellId
        if playerEntity.isMoving:
            self._followingMove = cell
            logger.debug("[RolePlayMovement] Player is already moving, waiting for him to stop")
            return False
        movePath = Pathfinding.findPath(DataMapProvider(), playerEntity.position, cell)
        self.sendPath(movePath)
        return True

    def sendPath(self, path: MovementPath) -> None:
        if path.start.cellId == path.end.cellId:
            if self.VERBOSE:
                logger.warn(
                    f"[RolePlayMovement] Discarding a movement path that begins and ends on the same cell ({path.start.cellId})."
                )
            logger.debug(
                f"[RolePlayMovement] following mosters {self._followingMonsterGroup}, followingIe {self._followingIe}"
            )
            self._isRequestingMovement = False
            if self._followingIe:
                self.activateSkill(
                    self._followingIe["skillInstanceId"],
                    self._followingIe["ie"],
                    self._followingIe["additionalParam"],
                )
                self._followingIe = None
            elif self._followingMonsterGroup:
                self._followingMonsterGroup = self.entitiesFrame.getEntityInfos(
                    self._followingMonsterGroup.contextualId
                )
                if self._followingMonsterGroup.disposition.cellId == path.end.cellId:
                    self.requestMonsterFight(self._followingMonsterGroup.contextualId)
                else:
                    self.askMoveTo(MapPoint.fromCellId(self._followingMonsterGroup.disposition.cellId))
            return
        gmmrmsg = GameMapMovementRequestMessage()
        keymoves = MapMovementAdapter.getServerMovement(path)
        gmmrmsg.init(keymoves, MapDisplayManager().currentMapPoint.mapId)
        logger.debug(f"[RolePlayMovement] Sending movement request with keymoves {keymoves}")
        ConnectionsHandler.getConnection().send(gmmrmsg)
        if self.VERBOSE:
            logger.debug(f"[RolePlayMovement] Movement request sent to server.")
        self._latestMovementRequest = perf_counter()

    def applyGameMapMovement(self, actorId: float, movement: MovementPath, forceWalking: bool = False) -> None:
        movedEntity: IEntity = DofusEntities.getEntity(actorId)
        if movedEntity is None:
            logger.warn(
                f"[RolePlayMovement] The entity {actorId} moved before it was added to the scene. Aborting movement."
            )
            return
        self._lastMoveEndCellId = movement.end.cellId
        if movedEntity.id == PlayedCharacterManager().id:
            self._isRequestingMovement = False

    def askMapChange(self) -> None:
        logger.debug("[RolePlayMovement] Asking for a map change to map " + str(self._wantToChangeMap))
        cmmsg: ChangeMapMessage = ChangeMapMessage()
        cmmsg.init(self._wantToChangeMap, self._changeMapByAutoTrip)
        ConnectionsHandler.getConnection().send(cmmsg)
        self._changeMapTimeout = Timer(5, self.onMapChangeFailed)
        self._changeMapTimeout.start()
        if self.VERBOSE:
            logger.debug("[RolePlayMovement] Change map timer started.")

    def attackMonsters(self, contextualId: int) -> None:
        entityInfo = self.entitiesFrame.getEntityInfos(contextualId)
        logger.debug("[RolePlayMovement] Asking for a fight against monsters " + str(entityInfo.contextualId))
        self.setFollowingMonsterFight(entityInfo)
        self.askMoveTo(MapPoint.fromCellId(entityInfo.disposition.cellId))

    def onMapChangeFailed(self) -> None:
        logger.debug(f"[RolePlayMovement] Map change failed, resetting to {self._wantToChangeMap}")
        if self._changeMapTimeout:
            self._changeMapTimeout.cancel()
        self._changeMapFails += 1
        if self._changeMapFails > 2:
            logger.debug(f"[RolePlayMovement] Change map to dest {self._wantToChangeMap} failed!")
            cmfm: MapChangeFailedMessage = MapChangeFailedMessage()
            cmfm.init(self._wantToChangeMap)
            Kernel().getWorker().processImmediately(cmfm)
        elif self._wantToChangeMap is None:
            logger.error(f"We want to change map to None, aborting")
        else:
            self.askMapChange()
            self._changeMapTimeout = Timer(3, self.onMapChangeFailed)
            self._changeMapTimeout.start()

    def activateSkill(self, skillInstanceId: int, ie: InteractiveElement, additionalParam: int) -> None:
        rpInteractivesFrame: rif.RoleplayInteractivesFrame = Kernel().getWorker().getFrame("RoleplayInteractivesFrame")
        if self.VERBOSE:
            logger.debug(
                f"[RolePlayMovement] requested registred Elm: {rpInteractivesFrame.currentRequestedElementId}, wants to activate {ie.elementId} and already using something {rpInteractivesFrame.usingInteractive}"
            )
        if (
            rpInteractivesFrame
            and rpInteractivesFrame.currentRequestedElementId != ie.elementId
            and not rpInteractivesFrame.usingInteractive
        ):
            rpInteractivesFrame.currentRequestedElementId = ie.elementId
            if additionalParam == 0:
                iurmsg = InteractiveUseRequestMessage()
                iurmsg.init(ie.elementId, skillInstanceId)
                ConnectionsHandler.getConnection().send(iurmsg)
            else:
                iuwprmsg = InteractiveUseWithParamRequestMessage()
                iuwprmsg.init(ie.elementId, skillInstanceId, additionalParam)
                ConnectionsHandler.getConnection().send(iuwprmsg)
            self._canMove = False

    def requestMonsterFight(self, monsterGroupId: int) -> None:
        if self._requestFighFails > 1:
            logger.error(f"Server rejected moster fight request for the {self._requestFighFails} time!")
            self._requestFighFails = 0
            nopmsg = FightRequestFailed()
            Kernel().getWorker().processImmediately(nopmsg)
            return False
        grpamrmsg: GameRolePlayAttackMonsterRequestMessage = GameRolePlayAttackMonsterRequestMessage()
        grpamrmsg.init(monsterGroupId)
        ConnectionsHandler.getConnection().send(grpamrmsg)
        self._requestFightTimeout = Timer(3, lambda: self.attackMonsters(monsterGroupId))
        self._requestFightTimeout.start()
        self._requestFighFails += 1
