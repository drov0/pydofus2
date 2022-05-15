import json
from threading import Timer
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.berilia.managers.KernelEventsManager import KernelEventsManager
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.modules.utils.pathFinding.world.Transition import Transition
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder
from com.ankamagames.dofus.network.messages.game.atlas.compass.CompassUpdatePartyMemberMessage import (
    CompassUpdatePartyMemberMessage,
)
from com.ankamagames.dofus.network.messages.game.chat.ChatClientPrivateMessage import ChatClientPrivateMessage
from com.ankamagames.dofus.network.messages.game.chat.ChatServerMessage import ChatServerMessage
from com.ankamagames.dofus.network.messages.game.context.fight.GameFightJoinRequestMessage import (
    GameFightJoinRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapChangeFailedMessage import MapChangeFailedMessage
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyAcceptInvitationMessage import (
    PartyAcceptInvitationMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyFollowMemberRequestMessage import (
    PartyFollowMemberRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyInvitationMessage import (
    PartyInvitationMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyInvitationRequestMessage import (
    PartyInvitationRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyJoinMessage import PartyJoinMessage
from com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyMemberInStandardFightMessage import (
    PartyMemberInStandardFightMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyNewMemberMessage import (
    PartyNewMemberMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyRefuseInvitationMessage import (
    PartyRefuseInvitationMessage,
)
from com.ankamagames.dofus.network.types.common.PlayerSearchCharacterNameInformation import (
    PlayerSearchCharacterNameInformation,
)
from com.ankamagames.dofus.network.types.game.context.MapCoordinates import MapCoordinates
from com.ankamagames.dofus.network.types.game.context.roleplay.party.PartyMemberInformations import (
    PartyMemberInformations,
)
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from pyd2bot.apis.MoveAPI import MoveAPI
from pyd2bot.logic.managers.SessionManager import SessionManager

from pyd2bot.logic.roleplay.frames.BotAutoTripFrame import BotAutoTripFrame
from pyd2bot.logic.roleplay.messages.AutoTripEndedMessage import AutoTripEndedMessage
from typing import TYPE_CHECKING

from pyd2bot.misc.BotEventsmanager import BotEventsManager

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import RoleplayEntitiesFrame
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame

logger = Logger("Dofus2")


class BotPartyFrame(Frame):
    ASK_INVITE_MSG = "Hello"
    OMW_MSG = "OMW"
    GO_MSG = "GO"
    ASK_INVITE_TIMOUT = 5
    CONFIRME_JOIN_TIMEOUT = 5
    name: str = None

    def __init__(self) -> None:
        super().__init__()

    @property
    def isLeader(self):
        return SessionManager().isLeader

    @property
    def followers(self):
        return SessionManager().followers

    @property
    def leaderName(self):
        return SessionManager().leaderName

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    @property
    def movementFrame(self) -> "RoleplayMovementFrame":
        return Kernel().getWorker().getFrame("RoleplayMovementFrame")

    @property
    def entitiesFrame(self) -> "RoleplayEntitiesFrame":
        return Kernel().getWorker().getFrame("RoleplayEntitiesFrame")

    @property
    def allMembersOnSameMap(self):
        mapPos = PlayedCharacterManager().currMapPos
        for follower in self.followers:
            if follower not in self._followerIds:
                return False
            member = self._partyMembers[self._followerIds[follower]]
            if mapPos.posX != member.worldX or mapPos.posY != member.worldY:
                return False
        return True

    def pulled(self):
        self.sendPrivateMessage(self.leaderName, "Goodby buddy. See you next time.")
        self._partyMembers.clear()
        if self.followers:
            self.followers.clear()
        if self._partyInviteTimers:
            self._partyInviteTimers.clear()
        return True

    def pushed(self):
        if self.isLeader is None:
            raise Exception("[BotPartyFrame] isLeader flag must be set")
        if self.isLeader and self.followers is None:
            raise Exception("[BotPartyFrame] followers must be defined for leaders")
        self._partyInviteTimers = dict[str, Timer]()
        self._partyId = None
        self._partyMembers = dict[int, PartyMemberInformations]()
        self._isJoiningLeaderVertex = False
        self._inParty = False
        self._allMemberOnSameMap = False
        self._allMembersJoined = False
        self._notifiedLeader = False
        self._wantsToJoinFight = None
        self._askInviteTimer = None
        self._followerIds = {}
        return True

    def sendPrivateMessage(self, playerName, message):
        ccmsg = ChatClientPrivateMessage()
        pi = PlayerSearchCharacterNameInformation()
        pi.init(playerName)
        ccmsg.init(pi, message)
        ConnectionsHandler.getConnection().send(ccmsg)

    def sendPartyInvite(self, playerName):
        pimsg = PartyInvitationRequestMessage()
        pscni = PlayerSearchCharacterNameInformation()
        pscni.init(playerName)
        pimsg.init(pscni)
        ConnectionsHandler.getConnection().send(pimsg)
        self._partyInviteTimers[playerName] = Timer(self.CONFIRME_JOIN_TIMEOUT, self.sendPartyInvite, [playerName])
        logger.debug(f"[BotPartyFrame] Invitation sent to {playerName}")

    def sendFollowMember(self, memberId):
        pfmrm = PartyFollowMemberRequestMessage()
        pfmrm.init(memberId, self._partyId)
        ConnectionsHandler.getConnection().send(pfmrm)

    def joinFight(self, fightId: int):
        if self.movementFrame._isMoving:
            self.movementFrame._wantsToJoinFight = {
                "fightId": fightId,
                "fighterId": self.leaderId,
            }
        else:
            self.movementFrame.joinFight(self.leaderId, fightId)

    def checkIfTeamInFight(self):
        if not PlayedCharacterManager().isFighting and self.entitiesFrame:
            for fightId, fight in self.entitiesFrame._fights.items():
                for team in fight.teams:
                    for member in team.teamInfos.teamMembers:
                        if member.id in self._partyMembers:
                            logger.debug(f"Team is in a fight")
                            self.joinFight(fightId)
                            return

    def process(self, msg: Message):

        if isinstance(msg, PartyInvitationMessage):
            if not self.isLeader and msg.fromName == self.leaderName:
                logger.debug(f"{msg.fromName} invited you to join his party")
                self.leaderId = msg.fromId
                self._partyId = msg.partyId
                paimsg = PartyAcceptInvitationMessage()
                paimsg.init(msg.partyId)
                ConnectionsHandler.getConnection().send(paimsg)
            elif msg.fromId != PlayedCharacterManager().id:
                pirmsg = PartyRefuseInvitationMessage()
                pirmsg.init(msg.partyId)
                ConnectionsHandler.getConnection().send(pirmsg)
            return True

        elif isinstance(msg, PartyNewMemberMessage):
            logger.info(f"{msg.memberInformations.name} joined your party")
            self._partyMembers[msg.memberInformations.id] = msg.memberInformations
            self._followerIds[msg.memberInformations.name] = msg.memberInformations.id
            if self.isLeader:
                self.sendFollowMember(msg.memberInformations.id)
                if msg.memberInformations.name in self._partyInviteTimers:
                    self._partyInviteTimers[msg.memberInformations.name].cancel()
                    del self._partyInviteTimers[msg.memberInformations.name]
            if self.isLeader and self.allMembersOnSameMap:
                BotEventsManager().dispatch(BotEventsManager.ALLMEMBERS_ONSAME_MAP)
            return True

        elif isinstance(msg, PartyJoinMessage):
            logger.debug(f"Party {msg.partyId} of leader {msg.partyLeaderId}")
            if self._askInviteTimer:
                self._askInviteTimer.cancel()
            if not self._inParty:
                self._inParty = True
                self._partyId = msg.partyId
                self.leaderId = msg.partyLeaderId
                if not self.isLeader:
                    self.sendFollowMember(self.leaderId)
            for member in msg.members:
                if member.id not in self._partyMembers:
                    self._partyMembers[member.id] = member
                if member.id != PlayedCharacterManager().id:
                    if self.isLeader:
                        self.sendFollowMember(member.id)
                    if member.name in self._partyInviteTimers:
                        logger.debug(f"The follower {member.name} has joined the party")
                        self._partyInviteTimers[member.name].cancel()
                        del self._partyInviteTimers[member.name]
            if not self.isLeader and not self._isJoiningLeaderVertex:
                if self.movementFrame:
                    self.movementFrame.setFollowingActor(self.leaderId)
                if (
                    PlayedCharacterManager().currentMap
                    and PlayedCharacterManager().currentMap.mapId != self._partyMembers[self.leaderId].mapId
                ):
                    self._isJoiningLeaderVertex = True
                    self.sendPrivateMessage(self.leaderName, self.OMW_MSG)
                    af = BotAutoTripFrame(self._partyMembers[self.leaderId].mapId)
                    Kernel().getWorker().pushFrame(af)
            if self.isLeader and all(member in self.followers for member in self._partyMembers):
                self._allMembersJoined = True
                logger.debug(f"All followers joined the party")
            if PlayedCharacterManager().currMapPos and self.isLeader and self.allMembersOnSameMap:
                BotEventsManager().dispatch(BotEventsManager.ALLMEMBERS_ONSAME_MAP)
            self.checkIfTeamInFight()
            return True

        elif isinstance(msg, AutoTripEndedMessage):
            if self._isJoiningLeaderVertex:
                leaderInfos = self.entitiesFrame.getEntityInfos(self.leaderId)
                if not leaderInfos:
                    raise Exception("Leader not found")
                leaderCellid = leaderInfos.disposition.cellId
                leaderRpZone = MapDisplayManager().dataMap.cells[leaderCellid].linkedZoneRP
                if leaderRpZone != PlayedCharacterManager().currentZoneRp:
                    af = BotAutoTripFrame(self._partyMembers[self.leaderId].mapId, leaderRpZone)
                    Kernel().getWorker().pushFrame(af)
                    return True
                self._isJoiningLeaderVertex = False
                self.sendPrivateMessage(self.leaderName, self.GO_MSG)
            elif self._wantsToJoinFight:
                self.joinFight(self._wantsToJoinFight)

        elif isinstance(msg, CompassUpdatePartyMemberMessage):
            self._partyMembers[msg.memberId].worldX = msg.coords.worldX
            self._partyMembers[msg.memberId].worldY = msg.coords.worldY
            dstMapId = MoveAPI.neighborMapIdFromcoords(msg.coords.worldX, msg.coords.worldY)
            logger.debug(f"Member {msg.memberId} moved to map {dstMapId}")
            mapPos = PlayedCharacterManager().currMapPos
            if self.isLeader and self.allMembersOnSameMap:
                BotEventsManager().dispatch(BotEventsManager.ALLMEMBERS_ONSAME_MAP)
            if not self.isLeader and not self._isJoiningLeaderVertex and msg.memberId == self.leaderId:
                logger.debug(f"Leader moved to map {dstMapId} will follow him")
                if mapPos.posX != msg.coords.worldX or mapPos.posY != msg.coords.worldY:
                    if self.movementFrame._isMoving:
                        self.movementFrame._wantToChangeMap = dstMapId
                    else:
                        MoveAPI.changeMapToDstCoords(msg.coords.worldX, msg.coords.worldY)

        elif isinstance(msg, ChatServerMessage):
            if self.isLeader and msg.senderName in self.followers and msg.content == self.ASK_INVITE_MSG:
                logger.debug(f"Follower {msg.senderName} asked to join the party")
                if msg.senderName not in self._partyInviteTimers:
                    self.sendPartyInvite(msg.senderName)
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            if self._partyId is None:
                if not self.isLeader and not self._notifiedLeader:
                    self.sendPrivateMessage(self.leaderName, self.ASK_INVITE_MSG)
                    logger.debug("{Notified} leader to ask join his group")
                    self._notifiedLeader = True
                    self._askInviteTimer = Timer(
                        self.ASK_INVITE_TIMOUT, self.sendPrivateMessage, [self.leaderName, self.ASK_INVITE_MSG]
                    )
                    self._askInviteTimer.start()

        elif isinstance(msg, PartyMemberInStandardFightMessage):
            if float(msg.memberId) == float(self.leaderId):
                logger.debug(f"member {msg.memberId} joined fight {msg.fightId}")
                if float(msg.fightMap.mapId) != float(PlayedCharacterManager().currentMap.mapId):
                    af = BotAutoTripFrame(msg.fightMap.mapId)
                    Kernel().getWorker().pushFrame(af)
                    self._wantsToJoinFight = msg.fightId
                else:
                    self.joinFight(msg.fightId)

        elif isinstance(msg, MapChangeFailedMessage):
            leaderPosX = self._partyMembers[self.leaderId].worldX
            leaderPosY = self._partyMembers[self.leaderId].worldY
            MoveAPI.changeMapToDstCoords(leaderPosX, leaderPosY)
