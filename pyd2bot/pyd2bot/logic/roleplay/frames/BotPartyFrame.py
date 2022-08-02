import json
import threading
from threading import Timer
from time import sleep
from typing import TYPE_CHECKING, Tuple
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Transition import Transition
from pyd2bot.logic.roleplay.messages.LeaderPosMessage import LeaderPosMessage
from pyd2bot.logic.roleplay.messages.LeaderTransitionMessage import LeaderTransitionMessage
from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Vertex import Vertex
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder
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
from thrift.transport.TTransport import TTransportException

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import RoleplayEntitiesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame
    from pyd2bot.logic.roleplay.frames.BotFarmPathFrame import BotFarmPathFrame
    from pyd2bot.logic.common.frames.BotWorkflowFrame import BotWorkflowFrame
    from thrift.transport.TTransport import TBufferedTransport
    from pyd2bot.thriftServer.pyd2botService.Pyd2botService import Client as Pyd2botServiceClient
    
lock = threading.Lock()
logger = Logger()


class MembersMonitor(threading.Thread):
    _runningMonitors = list['MembersMonitor']()
    VERBOSE = False
    def __init__(self, bpframe: "BotPartyFrame"):
        super().__init__()
        while self._runningMonitors:
            monitor = self._runningMonitors.pop()
            monitor.stopSig.set()
        self.bpframe = bpframe
        self.stopSig = threading.Event()
        self._runningMonitors.append(self)
        
    @property
    def wfframe(self) -> "BotWorkflowFrame":
        return Kernel().getWorker().getFrame("BotWorkflowFrame")
    
    def run(self) -> None:
        logger.debug("[MembersMonitor] started")
        while not self.stopSig.is_set():
            if PlayedCharacterManager().isInFight:
                if self.VERBOSE:
                    logger.debug("[MembersMonitor] bot isFighting")
            else:                
                if not self.bpframe:
                    if self.VERBOSE:
                        logger.debug("[MembersMonitor] BotPartyFrame not found")

                elif self.bpframe.allMembersIdle:
                    if self.bpframe.allMembersOnSameMap:
                        BotEventsManager().dispatch(BotEventsManager.MEMBERS_READY)
                    elif self.bpframe.farmFrame and self.bpframe.farmFrame.isInsideFarmPath and self.wfframe and self.wfframe.status() == "idle":
                        self.bpframe.notifyFollowesrWithPos()
            sleep(1)
        logger.debug("[MembersMonitor] died")
        if self in self._runningMonitors:
            self._runningMonitors.remove(self)

class BotPartyFrame(Frame):
    ASK_INVITE_TIMOUT = 10
    CONFIRME_JOIN_TIMEOUT = 5
    name: str = None
    changingMap: bool = False
    leaderTransitionsQueue : list = []
    followingLeaderTransition = None
    wantsTransition = None
    followersClients : dict[int, Tuple['TBufferedTransport', 'Pyd2botServiceClient']] = {}
    
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
    def workflowFrame(self) -> "BotWorkflowFrame":
        return Kernel().getWorker().getFrame("BotWorkflowFrame")
    
    @property
    def farmFrame(self) -> "BotFarmPathFrame":
        return Kernel().getWorker().getFrame("BotFarmPathFrame")
    
    @property
    def leader(self) -> dict:
        return SessionManager().leader
    
    @property
    def allMembersOnSameMap(self):
        for follower in self.followers:
            if self.entitiesFrame is None:
                return False
            entity = self.entitiesFrame.getEntityInfos(follower["id"])
            if not entity:
                return False
        return True
    
    @property
    def allMembersIdle(self):
        for follower in self.followers:
            follower["status"] = self.fetchFollowerStatus(follower)
            if follower["status"] != "idle":
                logger.debug(f"[BotPartyFrame] follower {follower['name']} is not idle but {follower['status']}")
                return False
        return True
    
    def pulled(self):
        if self.currentPartyId:
            self.leaveParty()
        if self.isLeader:
            self.canFarmMonitor.stopSig.set()
            self.canFarmMonitor.join()
        self.partyMembers.clear()
        if self._partyInviteTimers:
            for timer in self._partyInviteTimers.values():
                timer.cancel()
        self.currentPartyId = None
        self._partyInviteTimers.clear()
        self.leaderTransitionsQueue.clear()
        for transport, client in self.followersClients.values():
            transport.close()
        logger.debug("[BotPartyFrame] BotPartyFrame pulled")
        return True

    def pushed(self):
        logger.debug("[BotPartyFrame] BotPartyFrame pushed")
        self._partyInviteTimers = dict[str, Timer]()
        self.currentPartyId = None
        self.partyMembers = dict[int, PartyMemberInformations]()
        self.joiningLeaderVertex : Vertex = None
        self._allMemberOnSameMap = False
        self._allMembersJoined = False
        self._wantsToJoinFight = None
        self.leaderTransitionsQueue : list = []
        self.followingLeaderTransition = None
        if self.isLeader:
            logger.debug("[BotPartyFrame] Bot is leader")
            self.canFarmMonitor = MembersMonitor(self)
            self.canFarmMonitor.start()
            logger.debug(f"[BotPartyFrame] Send party invite to all followers {self.followers}")
            for follower in self.followers:
                follower["status"] = "unknown"
                self.connectFollowerClient(follower)
                logger.debug(f"[BotPartyFrame] Will Send party invite to {follower['name']}")
                self.sendPartyInvite(follower["name"])
        return True

    def getFollowerById(self, id: int) -> dict:
        for idx, follower in enumerate(self.followers):
            if follower["id"] == id:
                return follower
        return None 
    
    def sendPrivateMessage(self, playerName, message):
        ccmsg = ChatClientPrivateMessage()
        pi = PlayerSearchCharacterNameInformation()
        pi.init(playerName)
        ccmsg.init(pi, message)
        ConnectionsHandler.getConnection().send(ccmsg)

    def cancelPartyInvite(self, playerName):
        cpimsg = PartyCancelInvitationMessage()
        if self.currentPartyId is not None:
            for follower in self.followers:
                if follower["name"] == playerName:
                    cpimsg.init(follower["id"], self.currentPartyId)
                    ConnectionsHandler.getConnection().send(cpimsg)
                    break

    def sendPartyInvite(self, playerName):
        for member in self.partyMembers.values():
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
        pfmrm.init(memberId, self.currentPartyId)
        ConnectionsHandler.getConnection().send(pfmrm)

    def joinFight(self, fightId: int):
        if self.movementFrame._isMoving:
            self.movementFrame._wantsToJoinFight = {
                "fightId": fightId,
                "fighterId": self.leader['id'],
            }
        else:
            self.movementFrame.joinFight(self.leader['id'], fightId)

    def checkIfTeamInFight(self):
        if not PlayedCharacterManager().isFighting and self.entitiesFrame:
            for fightId, fight in self.entitiesFrame._fights.items():
                for team in fight.teams:
                    for member in team.teamInfos.teamMembers:
                        if member.id in self.partyMembers:
                            logger.debug(f"[BotPartyFrame] Team is in a fight")
                            self.joinFight(fightId)
                            return

    def leaveParty(self):
        if not self.currentPartyId:
            logger.warning("[BotPartyFrame] No party to leave")
            return
        plmsg = PartyLeaveRequestMessage()
        plmsg.init(self.currentPartyId)
        ConnectionsHandler.getConnection().send(plmsg)
        self.currentPartyId = None

    def process(self, msg: Message):
        
        if isinstance(msg, PartyNewGuestMessage):
            return True

        elif isinstance(msg, MapChangeFailedMessage):
            if self.isLeader:
                return False
            self.requestMapData()
            return True

        elif isinstance(msg, PartyMemberRemoveMessage):
            logger.debug(f"[BotPartyFrame] {msg.leavingPlayerId} left the party")
            player = self.partyMembers.get(msg.leavingPlayerId)
            if player:
                del self.partyMembers[msg.leavingPlayerId]
            if self.isLeader:
                follower = self.getFollowerById(msg.leavingPlayerId)
                self.sendPartyInvite(follower["name"])
            return True

        elif isinstance(msg, PartyDeletedMessage):
            if self.isLeader:
                for follower in self.followers:
                    self.sendPartyInvite(follower["name"])
            return True

        elif isinstance(msg, PartyInvitationMessage):
            logger.debug(f"[BotPartyFrame] {msg.fromName} invited you to join his party")
            if not self.isLeader and msg.fromName == self.leaderName:
                self.currentPartyId = msg.partyId
                paimsg = PartyAcceptInvitationMessage()
                paimsg.init(msg.partyId)
                ConnectionsHandler.getConnection().send(paimsg)
                logger.debug(f"[BotPartyFrame] accepted party invite from {msg.fromName}")
            elif msg.fromId != PlayedCharacterManager().id:
                pirmsg = PartyRefuseInvitationMessage()
                pirmsg.init(msg.partyId)
                ConnectionsHandler.getConnection().send(pirmsg)
            return True

        elif isinstance(msg, PartyNewMemberMessage):
            logger.info(f"[BotPartyFrame] {msg.memberInformations.name} joined your party")
            self.currentPartyId = msg.partyId
            self.partyMembers[msg.memberInformations.id] = msg.memberInformations
            if self.isLeader and msg.memberInformations.id != PlayedCharacterManager().id:
                self.sendFollowMember(msg.memberInformations.id)
                follower = self.getFollowerById(msg.memberInformations.id)
                # self.notifyFollowerWithPos(follower)
                if msg.memberInformations.name in self._partyInviteTimers:
                    self._partyInviteTimers[msg.memberInformations.name].cancel()
                    del self._partyInviteTimers[msg.memberInformations.name]
            elif msg.memberInformations.id == PlayedCharacterManager().id:
                self.sendFollowMember(self.leader['id'])
            return True
    
        elif isinstance(msg, PartyJoinMessage):
            self.partyMembers.clear()
            logger.debug(f"[BotPartyFrame] Party {msg.partyName} - {msg.partyId} of leader {msg.partyLeaderId}")
            if not self.isLeader and msg.partyLeaderId != self.leader["id"]:
                logger.warning(f"[BotPartyFrame] The party has the wrong leader {msg.partyLeaderId} instead of {self.leader['id']}")
                self.leaveParty()
                return
            for member in msg.members:
                if member.id not in self.partyMembers:
                    self.partyMembers[member.id] = member
                if member.id == PlayedCharacterManager().id:
                    if self.currentPartyId is None:
                        self.currentPartyId = msg.partyId
                        if not self.isLeader:
                            self.sendFollowMember(self.leader['id'])
            if not self.isLeader and self.joiningLeaderVertex is None:
                logger.debug(f"[BotPartyFrame] {self.leaderName} is in map {self.partyMembers[self.leader['id']].mapId}")
            self.checkIfTeamInFight()
            if not self.isLeader and self.leader['id'] not in self.partyMembers:
                self.leaveParty()
            return True

        elif isinstance(msg, AutoTripEndedMessage):
            if not self.isLeader and self.leader["id"] not in self.partyMembers:
                logger.warning(f"[BotPartyFrame] Leader {self.leaderName} is not in the party anymore!")
                return False
            if self.joiningLeaderVertex is not None:
                leaderInfos = self.entitiesFrame.getEntityInfos(self.leader["id"])
                if not leaderInfos:
                    logger.warning(f"[BotPartyFrame] Autotrip ended, was following leader transition {self.joiningLeaderVertex} but the leader {self.leaderName} is not in the current Map!")
                else:
                    self.leader["currentVertex"] = self.joiningLeaderVertex
                    self.joiningLeaderVertex = None
            if self._wantsToJoinFight:
                self.joinFight(self._wantsToJoinFight)

        elif isinstance(msg, LeaderTransitionMessage):
            logger.debug(f"[BotPartyFrame] Will follow {self.leader['name']} transit {msg.transition}")
            self.followingLeaderTransition = msg.transition
            MoveAPI.followTransition(msg.transition)
        
        elif isinstance(msg, LeaderPosMessage):
            self.leader["currentVertex"] = msg.vertex
            if self.joiningLeaderVertex is not None:
                if msg.vertex.UID == self.joiningLeaderVertex.UID:
                    return True
                else:
                    logger.warning(f"[BotPartyFrame] Received another leader pos {msg.vertex} while still following leader pos {self.joiningLeaderVertex}")
                    return True
            elif WorldPathFinder().currPlayerVertex is not None and  WorldPathFinder().currPlayerVertex.UID != msg.vertex.UID:
                logger.debug(f"[BotPartyFrame] Leader {self.leaderName} is in vertex {msg.vertex}, will follow it")
                self.joiningLeaderVertex = msg.vertex
                af = BotAutoTripFrame(msg.vertex.mapId, msg.vertex.zoneId)
                Kernel().getWorker().pushFrame(af)
                return True 
            else:
                logger.debug(f"[BotPartyFrame] Player is already in leader vertex {msg.vertex}")
            
        elif isinstance(msg, CompassUpdatePartyMemberMessage):
            self.partyMembers[msg.memberId].worldX = msg.coords.worldX
            self.partyMembers[msg.memberId].worldY = msg.coords.worldY
            logger.debug(f"[BotPartyFrame] Member {msg.memberId} moved to map {(msg.coords.worldX, msg.coords.worldY)}")
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            if not self.isLeader:
                logger.debug(f"*********************************** New map {msg.mapId}**********************************************")
                self.followingLeaderTransition = None

        elif isinstance(msg, PartyMemberInStandardFightMessage):
            if float(msg.memberId) == float(self.leader['id']):
                logger.debug(f"[BotPartyFrame] member {msg.memberId} started fight {msg.fightId}")
                if float(msg.fightMap.mapId) != float(PlayedCharacterManager().currentMap.mapId):
                    af = BotAutoTripFrame(msg.fightMap.mapId)
                    Kernel().getWorker().pushFrame(af)
                    self._wantsToJoinFight = msg.fightId
                else:
                    self.joinFight(msg.fightId)
            return True
        
    def setFollowLeader(self):
        if not self.isLeader:
            if not self.movementFrame:
                Timer(1, self.setFollowLeader).start()
                return
            self.movementFrame.setFollowingActor(self.leader['id'])
    
    def notifyFollowerWithPos(self, follower):
        cv = WorldPathFinder().currPlayerVertex
        if cv is None:
            Timer(1, self.notifyFollowerWithPos, [follower]).start()
            return
        
        transport, client = self.getFollowerClient(follower)
        if client is None:
            logger.warning(f"[BotPartyFrame] follower {follower['name']} thrift server is not connected.")
            raise Exception(f"follower {follower['name']} thrift server is not connected.")
        try:
            client.moveToVertex(json.dumps(cv.to_json()))
        except TTransportException as e:
            if e.message == "unexpected exception":
                logger.debug(f"[BotPartyFrame] follower {follower['name']} thrift server disconnected.")
                self.connectFollowerClient(follower)
                transport, client = self.getFollowerClient(follower)
                client.moveToVertex(json.dumps(cv.to_json()))     
            
    def notifyFollowersWithTransition(self, tr: Transition):
        for follower in self.followers:
            self.notifyFollowerWithTransition(follower, tr)
    
    def notifyFollowerWithTransition(self, follower: dict, tr: Transition):
        transport, client = self.getFollowerClient(follower)
        if client is None:
            logger.warning(f"[BotPartyFrame] follower {follower['name']} thrift server is not connected.")
            raise Exception(f"follower {follower['name']} thrift server is not connected.")
        try:
            client.followTransition(json.dumps(tr.to_json()))
        except TTransportException as e:
            if e.message == "unexpected exception":
                logger.debug(f"[BotPartyFrame] follower {follower['name']} thrift server disconnected.")
                self.connectFollowerClient(follower)
                transport, client = self.getFollowerClient(follower)
                client.followTransition(json.dumps(tr.to_json()))
                
    def notifyFollowesrWithPos(self):
        for follower in self.followers:
            self.notifyFollowerWithPos(follower)
            
    def fetchFollowerStatus(self, follower: dict):
        transport, client = self.getFollowerClient(follower)
        if client is None:
            logger.warning(f"[BotPartyFrame] follower {follower['name']} thrift server is not connected.")
            return "disconnected"
        try:
            return client.getStatus()
        except TTransportException as e:
            if e.message == "unexpected exception":
                logger.debug(f"[BotPartyFrame] follower {follower['name']} thrift server disconnected.")
                self.connectFollowerClient(follower)
                transport, client = self.getFollowerClient(follower)
                return client.getStatus()
            
    def requestMapData(self):
        mirmsg = MapInformationsRequestMessage()
        mirmsg.init(mapId_=MapDisplayManager().currentMapPoint.mapId)
        ConnectionsHandler.getConnection().send(mirmsg)

    def moveToVertex(self, vertex: Vertex):
        logger.debug(f"[BotPartyFrame] Moving to vertex {vertex}")
        self.joiningLeaderVertex = vertex
        af = BotAutoTripFrame(vertex.mapId, vertex.zoneId)
        Kernel().getWorker().pushFrame(af)
        return True
    
    def getFollowerClient(self, follower: dict):
        try:
            transport, client = self.followersClients[follower["id"]]
        except KeyError as e:
            return None, None
        try:
            if not transport.isOpen():
                transport.open()
        except TTransportException as e:
            if e.type == TTransportException.ALREADY_OPEN:
                pass
        return transport, client
    

    def connectFollowerClient(self, follower: dict):
        from pyd2bot.PyD2Bot import PyD2Bot

        transport, client = PyD2Bot().runClient('localhost', follower["serverPort"])
        self.followersClients[follower["id"]] = (transport, client)