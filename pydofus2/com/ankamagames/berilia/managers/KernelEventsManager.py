from enum import Enum

from pydofus2.com.ankamagames.berilia.managers.EventsHandler import \
    EventsHandler
from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.GameRolePlayHumanoidInformations import \
    GameRolePlayHumanoidInformations
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.types.positions.MovementPath import \
    MovementPath


class KernelEvent(Enum):
    MOVEMENT_STOPPED = 0
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
    PARTY_MEMBER_LEFT = 33
    INACTIVITY_WARNING = 34
class KernelEventsManager(EventsHandler, metaclass=Singleton):
    def __init__(self):
        super().__init__()

    def onFramePush(self, frameName, callback, args=[]):
        def onEvt(e, frame):
            if str(frame) == frameName:
                callback(*args)

        self.on(KernelEvent.FRAME_PUSHED, onEvt)

    def onceFramePushed(self, frameName, callback, args=[]):
        def onEvt(e, frame):
            if str(frame) == frameName:
                self.remove_listener(KernelEvent.FRAME_PUSHED, onEvt)
                callback(*args)

        self.on(KernelEvent.FRAME_PUSHED, onEvt)

    def onceFramePulled(self, frameName, callback, args=[]):
        def onEvt(e, frame):
            if str(frame) == frameName:
                self.remove_listener(KernelEvent.FRAME_PULLED, onEvt)
                callback(*args)

        self.on(KernelEvent.FRAME_PULLED, onEvt)
    
    def onceMapProcessed(self, callback, args=[], mapId=None):
        def onEvt(event, processedMapId):
            if mapId is not None:
                if processedMapId == mapId:
                    self.remove_listener(KernelEvent.MAPPROCESSED, onEvt)
                    callback(*args)
            else:
                callback(*args)
        if mapId is not None:
            self.on(KernelEvent.MAPPROCESSED, onEvt)
        else:
            self.once(KernelEvent.MAPPROCESSED, onEvt)
        return onEvt

    def send(self, event_id: KernelEvent, *args, **kwargs):
        if event_id == KernelEvent.CRASH:
            self._crashMessage = kwargs.get("message", None)
        super().send(event_id, *args, **kwargs)

    def onceActorShowed(self, actorId, callback, args=[]):
        def onActorShowed(event, infos: "GameRolePlayHumanoidInformations"):
            if int(actorId) == int(infos.contextualId):
                self.remove_listener(KernelEvent.ACTORSHOWED, onActorShowed)
                callback(*args)
        self.on(KernelEvent.ACTORSHOWED, onActorShowed)
    
    def onceEntityMoved(self, entityId, callback, args=[]):
        def onEntityMoved(e, movedEntityId, clientMovePath: MovementPath):
            if movedEntityId == entityId:
                self.remove_listener(KernelEvent.ENTITY_MOVED, onEntityMoved)
                callback(clientMovePath, *args)
        self.on(KernelEvent.ENTITY_MOVED, onEntityMoved)
        return onEntityMoved
    
    def onceEntityVanished(self, entityId, callback, args=[]):
        def onEntityVanished(e, vanishedEntityId):
            if vanishedEntityId == entityId:
                self.remove_listener(KernelEvent.ENTITY_VANISHED, onEntityVanished)
                callback(*args)
        self.on(KernelEvent.ENTITY_VANISHED, onEntityVanished)
        return onEntityVanished