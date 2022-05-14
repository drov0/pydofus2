from mimetypes import init
from operator import truediv
from threading import Timer
from com.ankamagames.dofus.datacenter.world.MapPosition import MapPosition
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.network.messages.game.atlas.compass.CompassUpdatePartyMemberMessage import (
    CompassUpdatePartyMemberMessage,
)
from com.ankamagames.dofus.network.messages.game.chat.ChatClientPrivateMessage import ChatClientPrivateMessage
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
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from pyd2bot.apis.MoveAPI import MoveAPI

from pyd2bot.logic.roleplay.frames.BotAutoTripFrame import BotAutoTripFrame
from pyd2bot.logic.roleplay.messages.AutoTripEndedMessage import AutoTripEndedMessage


class BotPartyFrame(Frame):
    leaderId: int
    followers: list[str]
    isLeader: bool
    leaderName: str

    def __init__(self) -> None:
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    def pulled(self):
        return True

    def pushed(self):
        self._partyInviteTimers = dict[str, Timer]()
        self._partyId = None
        self._partyMembers = dict[int, PartyMemberInformations]()
        self._isJoiningLeaderMap = False
        self._inParty = False
        self._allMemberOnSameMap = False
        self._allMembersJoined = False
        if self.isLeader:
            for follower in self.followers:
                self.sendPartyInvite(follower)
        else:
            self.sendPrivateMessage(self.leaderName, "I am in, invite me to your party :).")
        return True

    def sendPrivateMessage(self, playerName, message):
        if not PlayedCharacterManager().currentMap:
            Timer(1, self.sendPrivateMessage, [playerName, message]).start()
            return
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

    def process(self, msg: Message):

        if isinstance(msg, PartyInvitationMessage):
            if not self.isLeader and msg.fromId == self.leaderId:
                self._partyId = msg.partyId
                paimsg = PartyAcceptInvitationMessage()
                paimsg.init(msg.partyId)
                ConnectionsHandler.getConnection().send(paimsg)
            else:
                pirmsg = PartyRefuseInvitationMessage()
                pirmsg.init(msg.partyId)
                ConnectionsHandler.getConnection().send(pirmsg)

        elif isinstance(msg, PartyJoinMessage):
            if not self._inParty:
                self._inParty = True
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
            if not self.isLeader:
                if PlayedCharacterManager().currentMap.mapId != self._partyMembers[self.leaderId].mapId:
                    self._isJoiningLeaderMap = True
                    self.sendPrivateMessage(self.leaderName, "On my way.")
                    af = BotAutoTripFrame(self._partyMembers[self.leaderId].mapId)
                    Kernel().getWorker().pushFrame(af)
            if self.isLeader and len(msg.members) == len(self.followers) + 1:
                self._allMembersJoined = True

        elif isinstance(msg, AutoTripEndedMessage):
            if self._isJoiningLeaderMap:
                self._isJoiningLeaderMap = False

        elif isinstance(msg, CompassUpdatePartyMemberMessage):
            self._partyMembers[msg.memberId].worldX = msg.coords.worldX
            self._partyMembers[msg.memberId].worldY = msg.coords.worldY
            mapPos = PlayedCharacterManager().currMapPos
            self._allMemberOnSameMap = True
            for member in self._partyMembers.values():
                if mapPos.posX != msg.coords.worldX or mapPos.posY != msg.coords.worldY:
                    self._allMemberOnSameMap = False
                    break
            if not self.isLeader and msg.memberId == self.leaderId:
                self.sendPrivateMessage(self.leaderName, "On my way.")
                MoveAPI.changeMapToDstCoords(msg.coords.worldX, msg.coords.worldY)
