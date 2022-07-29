import json
import threading
from threading import Timer
from time import sleep
from typing import TYPE_CHECKING
from pydofus2.com.DofusClient import DofusClient

from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.logic.game.fight.messages.MapMoveFailed import MapMoveFailed
from pydofus2.com.ankamagames.dofus.network.messages.game.atlas.compass.CompassUpdatePartyMemberMessage import (
    CompassUpdatePartyMemberMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.chat.ChatClientPrivateMessage import ChatClientPrivateMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapChangeFailedMessage import MapChangeFailedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapInformationsRequestMessage import MapInformationsRequestMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyAcceptInvitationMessage import (
    PartyAcceptInvitationMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyCancelInvitationMessage import (
    PartyCancelInvitationMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyDeletedMessage import PartyDeletedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyFollowMemberRequestMessage import (
    PartyFollowMemberRequestMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyInvitationMessage import (
    PartyInvitationMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyInvitationRequestMessage import (
    PartyInvitationRequestMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyJoinMessage import PartyJoinMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyLeaveRequestMessage import (
    PartyLeaveRequestMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyMemberInStandardFightMessage import (
    PartyMemberInStandardFightMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyMemberRemoveMessage import (
    PartyMemberRemoveMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyNewGuestMessage import (
    PartyNewGuestMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyNewMemberMessage import (
    PartyNewMemberMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyRefuseInvitationMessage import (
    PartyRefuseInvitationMessage,
)
from pydofus2.com.ankamagames.dofus.network.types.common.PlayerSearchCharacterNameInformation import (
    PlayerSearchCharacterNameInformation,
)
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.party.PartyMemberInformations import (
    PartyMemberInformations,
)
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority
from pyd2bot.apis.MoveAPI import MoveAPI
from pyd2bot.logic.managers.SessionManager import SessionManager
from pyd2bot.logic.roleplay.frames.BotAutoTripFrame import BotAutoTripFrame
from pyd2bot.logic.roleplay.messages.AutoTripEndedMessage import AutoTripEndedMessage
from pyd2bot.misc.BotEventsmanager import BotEventsManager

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import RoleplayEntitiesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame

logger = Logger()


class AllOnSameMapMonitor(threading.Thread):
    _runningMonitors = list['AllOnSameMapMonitor']()
    def __init__(self, bpframe: "BotPartyFrame"):
        super().__init__()
        while self._runningMonitors:
            monitor = self._runningMonitors.pop()
            monitor.stopSig.set()
        self.bpframe = bpframe
        self.stopSig = threading.Event()
        self._runningMonitors.append(self)
        
    def run(self) -> None:
        logger.debug("AllOnSameMapMonitor started")
        while not self.stopSig.is_set():
            if PlayedCharacterManager().isInFight:
                logger.debug("AllOnSameMapMonitor: isFighting")
            else:                
                if not self.bpframe:
                    logger.debug("AllOnSameMapMonitor: No BotPartyFrame found")
                elif self.bpframe.allMembersOnSameMap:
                    BotEventsManager().dispatch(BotEventsManager.ALLMEMBERS_ONSAME_MAP)
                    logger.debug("AllOnSameMapMonitor: all members are on same map")
            sleep(1)
        logger.debug("AllOnSameMapMonitor: died")
        self._runningMonitors.remove(self)
        


class BotPartyFrame(Frame):
    ASK_INVITE_TIMOUT = 10
    CONFIRME_JOIN_TIMEOUT = 10
    name: str = None
    changingMap: bool = False
    mapChangesQueue = []

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
        return SessionManager().character["name"] if self.isLeader else SessionManager().leader["name"]

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
        for follower in self.followers:
            logger.debug(f"Checking follower if {follower['name']} is on same map")
            if self.entitiesFrame is None:
                logger.debug("No RoleplayEntitiesFrame found")
                return False
            entity = self.entitiesFrame.getEntityInfos(follower["id"])
            if not entity:
                logger.debug("Member %s not found in the current map", follower)
                return False
        logger.debug("All members are on the same map")
        return True

    def pulled(self):
        if self._inParty:
            self.leaveParty()
            self._inParty = False
        if self.isLeader:
            self.canFarmMonitor.stopSig.set()
            self.canFarmMonitor.join()
        self._partyMembers.clear()
        if self._partyInviteTimers:
            for timer in self._partyInviteTimers.values():
                timer.cancel()
        self._partyId = None
        self._partyInviteTimers.clear()
        self.mapChangesQueue.clear()
        logger.debug("BotPartyFrame pulled")
        return True

    def pushed(self):
        logger.debug("BotPartyFrame pushed")
        self._partyInviteTimers = dict[str, Timer]()
        self._partyId = None
        self._partyMembers = dict[int, PartyMemberInformations]()
        self._isJoiningLeaderVertex = False
        self._inParty = False
        self._allMemberOnSameMap = False
        self._allMembersJoined = False
        self._wantsToJoinFight = None
        if self.isLeader:
            logger.debug("Bot is leader")
            self.canFarmMonitor = AllOnSameMapMonitor(self)
            self.canFarmMonitor.start()
            logger.debug(f"Send party invite to all followers {self.followers}")
            for follower in self.followers:
                if follower["name"] == None or follower["id"] == None:
                    raise Exception("Follower name or id is None")
                self.sendPartyInvite(follower["name"])
        return True

    def sendPrivateMessage(self, playerName, message):
        ccmsg = ChatClientPrivateMessage()
        pi = PlayerSearchCharacterNameInformation()
        pi.init(playerName)
        ccmsg.init(pi, message)
        ConnectionsHandler.getConnection().send(ccmsg)

    def cancelPartyInvite(self, playerName):
        cpimsg = PartyCancelInvitationMessage()
        for follower in self.followers:
            if follower["name"] == playerName:
                cpimsg.init(follower["id"], self._partyId)
                ConnectionsHandler.getConnection().send(cpimsg)
                break

    def sendPartyInvite(self, playerName):
        for member in self._partyMembers.values():
            if member.name == playerName:
                return
        if self._partyInviteTimers.get(playerName):
            self._partyInviteTimers[playerName].cancel()
            self.cancelPartyInvite(playerName)
        pimsg = PartyInvitationRequestMessage()
        pscni = PlayerSearchCharacterNameInformation()
        pscni.init(playerName)
        pimsg.init(pscni)
        ConnectionsHandler.getConnection().send(pimsg)
        self._partyInviteTimers[playerName] = Timer(self.CONFIRME_JOIN_TIMEOUT, self.sendPartyInvite, [playerName])
        self._partyInviteTimers[playerName].start()
        logger.debug(f"[BotPartyFrame] Join party invitation sent to {playerName}")

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

    def leaveParty(self):
        plmsg = PartyLeaveRequestMessage()
        plmsg.init(self._partyId)
        ConnectionsHandler.getConnection().send(plmsg)

    def process(self, msg: Message):
        if isinstance(msg, PartyNewGuestMessage):
            return True

        elif isinstance(msg, MapMoveFailed):
            mirmsg = MapInformationsRequestMessage()
            mirmsg.init(mapId_=MapDisplayManager().currentMapPoint.mapId)
            ConnectionsHandler.getConnection().send(mirmsg)
            return True

        elif isinstance(msg, PartyMemberRemoveMessage):
            logger.debug(f"[BotPartyFrame] {msg.leavingPlayerId} left the party")
            playerName = self._partyMembers[msg.leavingPlayerId].name
            del self._partyMembers[msg.leavingPlayerId]
            if self.isLeader:
                self.sendPartyInvite(playerName)
            return True

        elif isinstance(msg, PartyDeletedMessage):
            if self.isLeader:
                for follower in self.followers:
                    self.sendPartyInvite(follower["name"])
            return True

        elif isinstance(msg, PartyInvitationMessage):
            logger.debug(f"{msg.fromName} invited you to join his party")
            if not self.isLeader and msg.fromName == self.leaderName:
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
            self._inParty = True
            self._partyId = msg.partyId
            self._partyMembers[msg.memberInformations.id] = msg.memberInformations
            if self.isLeader and msg.memberInformations.id != self.leaderId:
                self.sendFollowMember(msg.memberInformations.id)
                if msg.memberInformations.name in self._partyInviteTimers:
                    self._partyInviteTimers[msg.memberInformations.name].cancel()
                    del self._partyInviteTimers[msg.memberInformations.name]
            elif msg.memberInformations.id == PlayedCharacterManager().id:
                self.sendFollowMember(self.leaderId)
            return True

        elif isinstance(msg, PartyJoinMessage):
            self._partyMembers.clear()
            logger.debug(f"Party {msg.partyId} of leader {msg.partyLeaderId}")
            for member in msg.members:
                if member.id not in self._partyMembers:
                    self._partyMembers[member.id] = member
                if member.id == PlayedCharacterManager().id:
                    if not self._inParty:
                        self._inParty = True
                        self._partyId = msg.partyId
                        self.leaderId = msg.partyLeaderId
                        if not self.isLeader:
                            self.sendFollowMember(self.leaderId)
                    else:
                        for member in msg.members:
                            if member.id == msg.partyLeaderId:
                                if member.name != self.leaderName:
                                    self.leaveParty()
                                    return
            if not self.isLeader and not self._isJoiningLeaderVertex:
                logger.debug(f"{self.leaderName} is in map {self._partyMembers[self.leaderId].mapId}")
                self.setFollowLeader()
                if (
                    PlayedCharacterManager().currentMap
                    and PlayedCharacterManager().currentMap.mapId != self._partyMembers[self.leaderId].mapId
                ):
                    self._isJoiningLeaderVertex = True
                    af = BotAutoTripFrame(self._partyMembers[self.leaderId].mapId)
                    Kernel().getWorker().pushFrame(af)
                    return
            self.checkIfTeamInFight()
            if not self.isLeader and self.leaderId not in self._partyMembers:
                self.leaveParty()
            return True

        elif isinstance(msg, AutoTripEndedMessage):
            if self._isJoiningLeaderVertex:
                leaderInfos = self.entitiesFrame.getEntityInfos(self.leaderId)
                if not leaderInfos:
                    if self.leaderId not in self._partyMembers:
                        logger.warning(f"Leader {self.leaderName} is not in party anymore")
                        return False
                    af = BotAutoTripFrame(self._partyMembers[self.leaderId].mapId)
                    Kernel().getWorker().pushFrame(af)
                    return True
                leaderCellid = leaderInfos.disposition.cellId
                leaderRpZone = MapDisplayManager().dataMap.cells[leaderCellid].linkedZoneRP
                if leaderRpZone != PlayedCharacterManager().currentZoneRp:
                    af = BotAutoTripFrame(self._partyMembers[self.leaderId].mapId, leaderRpZone)
                    Kernel().getWorker().pushFrame(af)
                    return True
                self._isJoiningLeaderVertex = False
            elif self._wantsToJoinFight:
                self.joinFight(self._wantsToJoinFight)

        elif isinstance(msg, CompassUpdatePartyMemberMessage):
            self._partyMembers[msg.memberId].worldX = msg.coords.worldX
            self._partyMembers[msg.memberId].worldY = msg.coords.worldY
            logger.debug(f"Member {msg.memberId} moved to map {(msg.coords.worldX, msg.coords.worldY)}")
            mapPos = PlayedCharacterManager().currMapPos
            if not self.isLeader and not self._isJoiningLeaderVertex and msg.memberId == self.leaderId:
                logger.debug(
                    f"Leader moved to map {(msg.coords.worldX, msg.coords.worldY)}, my current pos {(mapPos.posX, mapPos.posY)} will follow him"
                )
                if mapPos.posX != msg.coords.worldX or mapPos.posY != msg.coords.worldY:
                    if self.movementFrame._isMoving:
                        self.movementFrame.cancelFollowingActor()
                    if self.changingMap:
                        logger.debug("Already changing map, queueing")
                        self.mapChangesQueue.append((msg.coords.worldX, msg.coords.worldY))
                    else:
                        MoveAPI.changeMapToDstCoords(msg.coords.worldX, msg.coords.worldY)
                        self.changingMap = True
            else:
                logger.debug("nothing to do")
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            self.changingMap = False
            if self.mapChangesQueue:
                cx, xy = self.mapChangesQueue.pop(0)
                MoveAPI.changeMapToDstCoords(cx, xy)
                self.changingMap = True
            elif self._partyId is not None and not self.isLeader:
                self.setFollowLeader()

        elif isinstance(msg, PartyMemberInStandardFightMessage):
            if float(msg.memberId) == float(self.leaderId):
                logger.debug(f"member {msg.memberId} joined fight {msg.fightId}")
                if (
                    self.movementFrame._wantToChangeMap is not None
                    and self.movementFrame._wantToChangeMap == msg.fightId
                ):
                    self.joinFight(msg.fightId)
                    return
                if float(msg.fightMap.mapId) != float(PlayedCharacterManager().currentMap.mapId):
                    af = BotAutoTripFrame(msg.fightMap.mapId)
                    Kernel().getWorker().pushFrame(af)
                    self._wantsToJoinFight = msg.fightId
                else:
                    self.joinFight(msg.fightId)
            return True

        elif isinstance(msg, MapChangeFailedMessage):
            leaderPosX = self._partyMembers[self.leaderId].worldX
            leaderPosY = self._partyMembers[self.leaderId].worldY
            MoveAPI.changeMapToDstCoords(leaderPosX, leaderPosY)
            self.changingMap = True

    def setFollowLeader(self):
        if not self.isLeader:
            if not self.movementFrame:
                Timer(1, self.setFollowLeader).start()
                return
            self.movementFrame.setFollowingActor(self.leaderId)
