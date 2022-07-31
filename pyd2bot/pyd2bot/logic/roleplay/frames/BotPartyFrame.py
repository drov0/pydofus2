import json
import threading
from threading import Timer
from time import sleep
from typing import TYPE_CHECKING
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import KernelEventsManager
from pydofus2.com.ankamagames.dofus.logic.game.roleplay.messages.CharacterMovementStoppedMessage import CharacterMovementStoppedMessage
from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Transition import Transition
from pyd2bot.logic.roleplay.messages.LeaderPosMessage import LeaderPosMessage
from pyd2bot.logic.roleplay.messages.LeaderTransitionMessage import LeaderTransitionMessage
from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.logic.game.fight.messages.MapMoveFailed import MapMoveFailed
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

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame import RoleplayEntitiesFrame
    from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import RoleplayMovementFrame
    from pyd2bot.logic.common.frames.BotWorkflowFrame import BotWorkflowFrame


logger = Logger()


class AllOnSameMapMonitor(threading.Thread):
    _runningMonitors = list['AllOnSameMapMonitor']()
    VERBOSE = False
    def __init__(self, bpframe: "BotPartyFrame"):
        super().__init__()
        while self._runningMonitors:
            monitor = self._runningMonitors.pop()
            monitor.stopSig.set()
        self.bpframe = bpframe
        self.stopSig = threading.Event()
        self._runningMonitors.append(self)
        
    def run(self) -> None:
        logger.debug("[AllOnSameMapMonitor] started")
        while not self.stopSig.is_set():
            if PlayedCharacterManager().isInFight:
                if self.VERBOSE:
                    logger.debug("[AllOnSameMapMonitor] bot isFighting")
            else:                
                if not self.bpframe:
                    if self.VERBOSE:
                        logger.debug("[AllOnSameMapMonitor] BotPartyFrame not found")
                elif self.bpframe.allMembersOnSameMap:
                    BotEventsManager().dispatch(BotEventsManager.ALLMEMBERS_ONSAME_MAP)
            sleep(1)
        logger.debug("[AllOnSameMapMonitor] died")
        self._runningMonitors.remove(self)
        


class BotPartyFrame(Frame):
    ASK_INVITE_TIMOUT = 10
    CONFIRME_JOIN_TIMEOUT = 10
    name: str = None
    changingMap: bool = False
    leaderTransitionsQueue : list = []
    followingLeaderTransition = None
    wantsTransition = None
    
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
    def leader(self) -> dict:
        return SessionManager().leader
    
    @property
    def allMembersOnSameMap(self):
        for follower in self.followers:
            # logger.debug(f"[BotPartyFrame] Checking follower if {follower['name']} is on same map")
            if self.entitiesFrame is None:
                # logger.debug("[BotPartyFrame] No RoleplayEntitiesFrame found")
                return False
            entity = self.entitiesFrame.getEntityInfos(follower["id"])
            if not entity:
                # logger.debug(f"[BotPartyFrame] Member {follower['name']} not found in the current map")
                return False
        # logger.debug("[BotPartyFrame] All members are on the same map")
        return True

    def pulled(self):
        if self.currentPartyId:
            self.leaveParty()
        if self.isLeader:
            self.canFarmMonitor.stopSig.set()
            self.canFarmMonitor.join()
        self._partyMembers.clear()
        if self._partyInviteTimers:
            for timer in self._partyInviteTimers.values():
                timer.cancel()
        self.currentPartyId = None
        self._partyInviteTimers.clear()
        self.leaderTransitionsQueue.clear()
        logger.debug("[BotPartyFrame] BotPartyFrame pulled")
        return True

    def pushed(self):
        logger.debug("[BotPartyFrame] BotPartyFrame pushed")
        self._partyInviteTimers = dict[str, Timer]()
        self.currentPartyId = None
        self._partyMembers = dict[int, PartyMemberInformations]()
        self._joiningLeaderVertex : Vertex = None
        self._allMemberOnSameMap = False
        self._allMembersJoined = False
        self._wantsToJoinFight = None
        self.leaderTransitionsQueue : list = []
        self.followingLeaderTransition = None
        if self.isLeader:
            logger.debug("[BotPartyFrame] Bot is leader")
            self.canFarmMonitor = AllOnSameMapMonitor(self)
            self.canFarmMonitor.start()
            logger.debug(f"[BotPartyFrame] Send party invite to all followers {self.followers}")
            for follower in self.followers:
                if follower["name"] is None or follower["id"] is None:
                    raise Exception("Follower name or id is None")
                logger.debug(f"[BotPartyFrame] Will Send party invite to {follower['name']}")
                self.sendPartyInvite(follower["name"])
        return True

    def getFollowerById(self, id: int) -> dict:
        for idx, follower in enumerate(self.followers):
            if follower["id"] == id:
                return idx
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
                        if member.id in self._partyMembers:
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
        
        if self.workflowFrame._inBankAutoUnload:
            return False
        
        if isinstance(msg, PartyNewGuestMessage):
            return True

        elif isinstance(msg, MapChangeFailedMessage):
            if self.isLeader:
                return False
            if self.followingLeaderTransition:
                self.leaderTransitionsQueue = [self.followingLeaderTransition] + self.leaderTransitionsQueue
                self.followingLeaderTransition = None
            self.requestMapData()
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
            logger.debug(f"[BotPartyFrame] {msg.fromName} invited you to join his party")
            if not self.isLeader and msg.fromName == self.leaderName:
                self.leader['id'] = msg.fromId
                self.currentPartyId = msg.partyId
                paimsg = PartyAcceptInvitationMessage()
                paimsg.init(msg.partyId)
                ConnectionsHandler.getConnection().send(paimsg)
            elif msg.fromId != PlayedCharacterManager().id:
                pirmsg = PartyRefuseInvitationMessage()
                pirmsg.init(msg.partyId)
                ConnectionsHandler.getConnection().send(pirmsg)
            return True

        elif isinstance(msg, PartyNewMemberMessage):
            logger.info(f"[BotPartyFrame] {msg.memberInformations.name} joined your party")
            self.currentPartyId = msg.partyId
            self._partyMembers[msg.memberInformations.id] = msg.memberInformations
            if self.isLeader and msg.memberInformations.id != PlayedCharacterManager().id:
                self.sendFollowMember(msg.memberInformations.id)
                fidx = self.getFollowerById(msg.memberInformations.id)
                self.notifyFollowerWithPos(fidx)
                if msg.memberInformations.name in self._partyInviteTimers:
                    self._partyInviteTimers[msg.memberInformations.name].cancel()
                    del self._partyInviteTimers[msg.memberInformations.name]
            elif msg.memberInformations.id == PlayedCharacterManager().id:
                self.sendFollowMember(self.leader['id'])
            return True
    
        elif isinstance(msg, PartyJoinMessage):
            self._partyMembers.clear()
            logger.debug(f"[BotPartyFrame] Party {msg.partyId} of leader {msg.partyLeaderId}")
            for member in msg.members:
                if member.id not in self._partyMembers:
                    self._partyMembers[member.id] = member
                if member.id == PlayedCharacterManager().id:
                    if not self.currentPartyId:
                        self.currentPartyId = msg.partyId
                        if not self.isLeader:
                            self.sendFollowMember(self.leader['id'])
                    elif msg.partyLeaderId != self.leader["id"]:
                        logger.warning(f"[BotPartyFrame] The party has the wrong leader {msg.partyLeaderId} instead of {self.leader['id']}")
                        self.leaveParty()
                        return
            if not self.isLeader and self._joiningLeaderVertex is None:
                logger.debug(f"[BotPartyFrame] {self.leaderName} is in map {self._partyMembers[self.leader['id']].mapId}")
            self.checkIfTeamInFight()
            if not self.isLeader and self.leader['id'] not in self._partyMembers:
                self.leaveParty()
            return True

        elif isinstance(msg, AutoTripEndedMessage):
            if self._joiningLeaderVertex is not None:
                leaderInfos = self.entitiesFrame.getEntityInfos(self.leader["id"])
                if not leaderInfos:
                    logger.warning(f"[BotPartyFrame] Autotrip ended, was following leader transition {self._joiningLeaderVertex} but the leader {self.leaderName} is not in the current Map!")
                    if self.leader["id"] not in self._partyMembers:
                        logger.warning(f"[BotPartyFrame] Leader {self.leaderName} is not in the party anymore!")
                        return False
                    if PlayedCharacterManager().currentMap.mapId != self._joiningLeaderVertex.mapId:
                        logger.warning(f"[BotPartyFrame] Leader {self.leaderName} is not in the correct map!")
                        af = BotAutoTripFrame(self._joiningLeaderVertex.mapId, self._joiningLeaderVertex.zoneId)
                        Kernel().getWorker().pushFrame(af)
                        return True
                else:
                    self.leader["currentVertex"] = self._joiningLeaderVertex
                    self._joiningLeaderVertex = None
            if self._wantsToJoinFight:
                self.joinFight(self._wantsToJoinFight)

        elif isinstance(msg, LeaderTransitionMessage):
            logger.debug(f"[BotPartyFrame] Leader {self.leader['name']} will transit following {msg.transition}")
            if self.followingLeaderTransition is None:
                self.wantsTransition = msg.transition
                if self.movementFrame._isMoving:
                    KernelEventsManager().add_listener(KernelEventsManager.MOVEMENT_STOPPED, self.onMovementStopped)
                    logger.debug(f"[BotPartyFrame] Leader transited but the bot is still moving, waiting for the end of the movement")
                else:
                    self.onMovementStopped(None)
            elif self.followingLeaderTransition != msg.transition:
                logger.debug(f"[BotPartyFrame] Bot is already following {self.followingLeaderTransition}. Will queue this one!")
                self.leaderTransitionsQueue.append(msg.transition)
        
        elif isinstance(msg, LeaderPosMessage):
            self.leader["currentVertex"] = msg.vertex
            if self._joiningLeaderVertex is not None:
                if msg.vertex.UID == self._joiningLeaderVertex.UID:
                    return True
            elif WorldPathFinder().currPlayerVertex != msg.vertex:
                self._joiningLeaderVertex = msg.vertex
                af = BotAutoTripFrame(msg.vertex.mapId, msg.vertex.zoneId)
                Kernel().getWorker().pushFrame(af)
                return True 
            
        elif isinstance(msg, CompassUpdatePartyMemberMessage):
            self._partyMembers[msg.memberId].worldX = msg.coords.worldX
            self._partyMembers[msg.memberId].worldY = msg.coords.worldY
            logger.debug(f"[BotPartyFrame] Member {msg.memberId} moved to map {(msg.coords.worldX, msg.coords.worldY)}")
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            if not self.isLeader:
                self.followingLeaderTransition = None
                if self.leaderTransitionsQueue:
                    tr = self.leaderTransitionsQueue.pop(0)
                    self.followingLeaderTransition = tr
                    MoveAPI.followTransition(tr)

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
    
    def sendMsgToFollower(self, msg: dict, followerIdx: int):
        follower = self.followers[followerIdx]
        port = follower["serverPort"]
        logger.debug(f"[BotPartyFrame] Sending message {msg} to follower {port}")
        from pyd2bot.PyD2Bot import PyD2Bot
        transport, client = PyD2Bot().runClient('localhost', port)
        recv = client.rcvLeaderMsg(json.dumps(msg))
        logger.debug(f"[BotPartyFrame] Received message {recv} from follower {port}")
        transport.close()
        return recv
    
    def notifyFollowerWithPos(self, followerIdx):
        cv = WorldPathFinder().currPlayerVertex
        if cv is None:
            Timer(1, self.notifyFollowerWithPos, [followerIdx]).start()
            return
        msg = {
            "type": "pos",
            "data": cv.to_json()
        }
        try:
            rcv = self.sendMsgToFollower(msg, followerIdx)
        except Exception as e:
            logger.warning(f"[BotPartyFrame] Exception while sending pos to follower {followerIdx}")
            logger.warning(e)
            return False
        followerPos = json.loads(rcv)
        self.followers[followerIdx]["currentVertex"] = Vertex(**followerPos["vertex"])
        self.followers[followerIdx]["currentCellId"] = followerPos["cellid"]
            
            
    def notifyFollowersWithTransition(self, tr: Transition):
        for followerIdx, follower in enumerate(self.followers):
            msg = {
                "type": "transit",
                "data": tr.to_json()
            }
            rcv = self.sendMsgToFollower(msg, followerIdx)
            followerPos = json.loads(rcv)
            self.followers[followerIdx]["currentVertex"] = Vertex(**followerPos["vertex"])
            self.followers[followerIdx]["currentCellId"] = followerPos["cellid"]
    
    def onMovementStopped(self, event):
        KernelEventsManager().remove_listener(KernelEventsManager.MOVEMENT_STOPPED, self.onMovementStopped)
        logger.debug(f"[BotPartyFrame] Movement stopped")
        if self.wantsTransition is not None:
            logger.debug(f"[BotPartyFrame] Wants to follow transition {self.wantsTransition}")
            self.followingLeaderTransition = self.wantsTransition
            self.wantsTransition = None
            MoveAPI.followTransition(self.followingLeaderTransition)
            
    def requestMapData(self):
        mirmsg = MapInformationsRequestMessage()
        mirmsg.init(mapId_=MapDisplayManager().currentMapPoint.mapId)
        ConnectionsHandler.getConnection().send(mirmsg)