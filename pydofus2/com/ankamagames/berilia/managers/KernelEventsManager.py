from enum import Enum
from time import perf_counter

from pydofus2.com.ankamagames.berilia.managers.EventsHandler import (
    Event, EventsHandler, Listener)
from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.FightCommonInformations import \
    FightCommonInformations
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayHumanoidInformations import \
    GameRolePlayHumanoidInformations
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.party.PartyMemberInformations import \
    PartyMemberInformations
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.types.positions.MovementPath import \
    MovementPath


class KernelEvent(Enum):
    MOVE_REQUEST_REJECTED = 0
    SERVERS_LIST = 1
    CHARACTERS_LIST = 2
    CRASH = 3
    LOGGED_IN = 4
    IN_GAME = 5
    DEAD = 6
    ALIVE = 7
    ACTORSHOWED = 8
    CHARACTER_SELECTION_SUCCESS = 9
    SHUTDOWN = 10
    RESTART = 11
    MAPLOADED = 12
    MAPPROCESSED = 13
    FRAME_PUSHED = 14
    FRAME_PULLED = 15
    RECONNECT = 16
    FIGHT_RESUMED = 17
    FIGHTER_MOVEMENT_APPLIED = 18
    FIGHTER_CASTED_SPELL = 19
    SEQUENCE_EXEC_FINISHED = 20
    PHENIX_AUTO_REVIVE_ENDED = 21
    AUTO_TRIP_ENDED = 22
    INVENTORY_UNLOADED = 23
    FIGHT_STARTED = 24
    FIGHT_ENDED = 30
    INTERACTIVE_ELEMENT_BEING_USED = 25
    INTERACTIVE_ELEMENT_USED = 26
    INTERACTIVE_USE_ERROR = 27
    PLAYER_STATE_CHANGED = 28
    ENTITY_MOVED = 29
    ENTITY_VANISHED = 31
    FULL_PODS = 32
    INACTIVITY_WARNING = 34
    LEVEL_UP = 35
    CHARACTER_STATS = 36
    RELOGIN_TOKEN = 37
    CHARACTER_NAME_SUGGESTION = 38
    CHARACTER_NAME_SUGGESTION_FAILED = 46
    CHARACTER_CREATION_RESULT = 39
    NPC_DIALOG_OPEN = 40
    NPC_QUESTION = 41
    NPC_DIALOG_LEFT = 43
    INVENTORY_WEIGHT_UPDATE = 42
    EXCHANGE_OPEN = 44
    EXCHANGE_CLOSE = 45
    QUEST_START = 47
    CHAR_DEL_PREP = 48
    TEXT_INFO = 49
    FIGHT_SWORD_SHOWED = 50
    CURRENT_MAP = 51
    MULE_FIGHT_CONTEXT = 52
    I_JOINED_PARTY = 53
    MEMBER_JOINED_PARTY = 54
    MEMBER_LEFT_PARTY = 55
    PARTY_DELETED = 56
    PARTY_INVITATION = 57
    PARTY_MEMBER_IN_FIGHT = 58
    PARTY_JOIN_FAILED = 59
    PARTY_INVITE_CANCEL_NOTIF = 60
    KAMAS_UPDATE = 61
    INTERACTIVE_ELEM_UPDATE = 62

class KernelEventsManager(EventsHandler, metaclass=Singleton):
    def __init__(self):
        super().__init__()

    def onFramePush(self, frameName, callback, args=[], originator=None):
        def onEvt(e, frame):
            if str(frame) == frameName:
                callback(*args)

        return self.on(KernelEvent.FRAME_PUSHED, onEvt, originator=originator)

    def onceFramePushed(self, frameName, callback, args=[], originator=None):
        def onEvt(evt: Event, frame):
            if str(frame) == frameName:
                evt.listener.delete()
                callback(*args)

        return self.on(KernelEvent.FRAME_PUSHED, onEvt, originator=originator)

    def onceFramePulled(self, frameName, callback, args=[], originator=None):
        def onEvt(e: Event, frame):
            if str(frame) == frameName:
                e.listener.delete()
                callback(*args)
        return self.on(KernelEvent.FRAME_PULLED, onEvt, originator=originator)

    def onceMapProcessed(
        self, callback, args=[], mapId=None, timeout=None, ontimeout=None, originator=None
    ) -> "Listener":
        once = mapId is None
        startTime = perf_counter()
        def onEvt(event: Event, processedMapId):
            if mapId is not None:
                if processedMapId == mapId:
                    event.listener.delete()
                    return callback(*args)
                if timeout:
                    remaining = timeout - (perf_counter() - startTime)
                    if remaining > 0:
                        event.listener.armTimer(remaining)
                    else:
                        ontimeout(event.listener)
            else:
                callback(*args)
        return self.on(
            KernelEvent.MAPPROCESSED, onEvt, once=once, timeout=timeout, ontimeout=ontimeout, originator=originator
        )

    def send(self, event_id: KernelEvent, *args, **kwargs):
        if event_id == KernelEvent.CRASH:
            self._crashMessage = kwargs.get("message", None)
        super().send(event_id, *args, **kwargs)

    def onceActorShowed(self, actorId, callback, args=[], originator=None):
        def onActorShowed(event: Event, infos: "GameRolePlayHumanoidInformations"):
            if int(actorId) == int(infos.contextualId):
                event.listener.delete()
                callback(*args)
        return self.on(KernelEvent.ACTORSHOWED, onActorShowed, originator=originator)

    def onEntityMoved(self, entityId, callback, timeout=None, ontimeout=None, once=False, originator=None):
        startTime = perf_counter()
        def onEntityMoved(event: Event, movedEntityId, clientMovePath: MovementPath):
            if movedEntityId == entityId:
                if once:
                    event.listener.delete()
                return callback(event, clientMovePath)
            if timeout:
                remaining = timeout - (perf_counter() - startTime)
                if remaining > 0:
                    event.listener.armTimer(remaining)
                else:
                    ontimeout(event.listener)
        return self.on(KernelEvent.ENTITY_MOVED, onEntityMoved, timeout=timeout, ontimeout=ontimeout, originator=originator)

    def onceEntityMoved(self, entityId, callback, timeout=None, ontimeout=None, originator=None):
        return self.onEntityMoved(entityId, callback, timeout=timeout, ontimeout=ontimeout, once=True, originator=originator)

    def onceEntityVanished(self, entityId, callback, args=[], originator=None):
        def onEntityVanished(event: Event, vanishedEntityId):
            if vanishedEntityId == entityId:
                event.listener.delete()
                callback(*args)
        return self.on(KernelEvent.ENTITY_VANISHED, onEntityVanished, originator=originator)

    def onceFightSword(self, entityId, entityCell, callback, args=[], originator=None):
        def onFightSword(event: Event, infos: FightCommonInformations):
            for team in infos.fightTeams:
                if team.leaderId == entityId and infos.fightTeamsPositions[team.teamId] == entityCell:
                    event.listener.delete()
                    callback(*args)
        return self.on(KernelEvent.FIGHT_SWORD_SHOWED, onFightSword, originator=originator)

    def onceFightStarted(self, callback, timeout, ontimeout, originator=None):
        return self.on(KernelEvent.FIGHT_STARTED, callback, timeout=timeout, ontimeout=ontimeout, once=True, originator=originator)

    def onceMemberJoinedParty(self, memberId, callback, args=[], timeout=None, ontimeout=None, originator=None):
        startTime = perf_counter()
        def onNewMember(event: Event, partyId, member: PartyMemberInformations):
            if member.id == memberId:
                event.listener.delete()
                return callback(*args)
            if timeout:
                remaining = timeout - (perf_counter() - startTime)
                if remaining > 0:
                    event.listener.armTimer(remaining)
                else:
                    ontimeout(event.listener)
        KernelEventsManager().on(KernelEvent.MEMBER_JOINED_PARTY, onNewMember, timeout=None, ontimeout=None, originator=originator)