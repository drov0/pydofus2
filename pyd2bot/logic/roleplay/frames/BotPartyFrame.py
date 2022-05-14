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

from pyd2bot.logic.roleplay.frames.BotAutoTripFrame import BotAutoTripFrame
from pyd2bot.logic.roleplay.messages.AutoTripEndedMessage import AutoTripEndedMessage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import RoleplayEntitiesFrame
    from com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame

logger = Logger("Dofus2")


class BotPartyFrame(Frame):
    leaderId: int
    followers: list[str] = None
    isLeader: bool
    leaderName: str = None
    _followerConnected = None

    def __init__(self) -> None:
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    @property
    def movementFrame(self) -> "RoleplayMovementFrame":
        return Kernel().getWorker().getFrame("RoleplayMovementFrame")

    @property
    def entitiesFrame(self) -> "RoleplayEntitiesFrame":
        return Kernel().getWorker().getFrame("RoleplayEntitiesFrame")

    def pulled(self):
        self.sendPrivateMessage(self.leaderName, "Goodby buddy. See you next time.")
        self._partyMembers.clear()
        if self.followers:
            self.followers.clear()
        if self._partyInviteTimers:
            self._partyInviteTimers.clear()
        if self._followerConnected:
            self._followerConnected.clear()
        return True

    def pushed(self):
        if self.isLeader is None:
            raise Exception("BotPartyFrame isLeader must be defined")
        if self.isLeader and self.followers is None:
            raise Exception("BotPartyFrame followers must be defined for leaders")
        self._partyInviteTimers = dict[str, Timer]()
        self._partyId = None
        self._partyMembers = dict[int, PartyMemberInformations]()
        self._isJoiningLeaderVertex = False
        self._inParty = False
        self._allMemberOnSameMap = False
        self._allMembersJoined = False
        self._notifiedLeader = False
        self._wantsToJoinFight = None
        if self.isLeader:
            self._followerConnected = dict[str, bool]({name: False for name in self.followers})
        return True

    def notifyMembersWithTransition(self, tr: Transition):
        for follower in self.followers:
            self.sendPrivateMessage(follower, f"Transition {json.dumps(tr.to_json())}")

    def sendPrivateMessage(self, playerName, message):
        ccmsg = ChatClientPrivateMessage()
        pi = PlayerSearchCharacterNameInformation()
        pi.init(self.leaderName)
        ccmsg.init(pi, message)
        ConnectionsHandler.getConnection().send(ccmsg)

    def sendPartyInvite(self, playerName):
        pimsg = PartyInvitationRequestMessage()
        pscni = PlayerSearchCharacterNameInformation()
        pscni.init(playerName)
        pimsg.init(pscni)
        ConnectionsHandler.getConnection().send(pimsg)
        self._partyInviteTimers[playerName] = Timer(5, self.sendPartyInvite, [playerName])

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
                self.leaderId = msg.fromId
                self._partyId = msg.partyId
                paimsg = PartyAcceptInvitationMessage()
                paimsg.init(msg.partyId)
                ConnectionsHandler.getConnection().send(paimsg)
            else:
                pirmsg = PartyRefuseInvitationMessage()
                pirmsg.init(msg.partyId)
                ConnectionsHandler.getConnection().send(pirmsg)

        elif isinstance(msg, PartyJoinMessage):
            logger.debug(f"PartyJoinMessage {msg.partyId} of leader {msg.partyLeaderId}")
            if not self._inParty:
                self._inParty = True
                self._partyId = msg.partyId
                self.leaderId = msg.partyLeaderId
                if not self.isLeader:
                    self.sendFollowMember(self.leaderId)
            for member in msg.members:
                if member.id not in self._partyMembers:
                    self._partyMembers[member.id] = member
                    if self.isLeader:
                        self.sendFollowMember(member.id)
                if member.name in self._partyInviteTimers:
                    self._partyInviteTimers[member.name].cancel()
                    del self._partyInviteTimers[member.name]
            if not self.isLeader and not self._isJoiningLeaderVertex:
                if (
                    PlayedCharacterManager().currentMap
                    and PlayedCharacterManager().currentMap.mapId != self._partyMembers[self.leaderId].mapId
                ):
                    self._isJoiningLeaderVertex = True
                    self.sendPrivateMessage(self.leaderName, "J'arrive attends que je soit dans ta map pls.")
                    af = BotAutoTripFrame(self._partyMembers[self.leaderId].mapId)
                    Kernel().getWorker().pushFrame(af)
            if self.isLeader and len(msg.members) == len(self.followers) + 1:
                self._allMembersJoined = True
            self.checkIfTeamInFight()

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
                self.sendPrivateMessage(self.leaderName, "Je suis laaa :). Go fight!.")
            elif self._wantsToJoinFight:
                self.joinFight(self._wantsToJoinFight)

        elif isinstance(msg, CompassUpdatePartyMemberMessage):
            self._partyMembers[msg.memberId].worldX = msg.coords.worldX
            self._partyMembers[msg.memberId].worldY = msg.coords.worldY
            dstMapId = MoveAPI.neighborMapIdFromcoords(msg.coords.worldX, msg.coords.worldY)
            logger.debug(f"member {msg.memberId} moved to map {dstMapId}")
            mapPos = PlayedCharacterManager().currMapPos
            self._allMemberOnSameMap = True
            for member in self._partyMembers.values():
                if mapPos.posX != msg.coords.worldX or mapPos.posY != msg.coords.worldY:
                    self._allMemberOnSameMap = False
                    break
            if not self.isLeader and not self._isJoiningLeaderVertex and msg.memberId == self.leaderId:
                logger.debug(f"Leader moved to map {dstMapId} will follow him")
                if mapPos.posX != msg.coords.worldX or mapPos.posY != msg.coords.worldY:
                    if self.movementFrame._isMoving:
                        self.movementFrame._wantToChangeMap = dstMapId
                    else:
                        MoveAPI.changeMapToDstCoords(msg.coords.worldX, msg.coords.worldY)

        elif isinstance(msg, ChatServerMessage):
            if self.isLeader and msg.senderName in self.followers:
                if msg.senderName not in self._partyInviteTimers:
                    self.sendPartyInvite(msg.senderName)
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            if self._partyId is None:
                if not self._notifiedLeader:
                    self.sendPrivateMessage(self.leaderName, "I am in. Invite me to your party :).")
                    logger.debug("Notified leader to ask join his group")
                    self._notifiedLeader = True
            if self.movementFrame:
                self.movementFrame.setFollowingActor(self.leaderId)

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
