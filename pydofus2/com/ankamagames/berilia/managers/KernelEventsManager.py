import threading
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from whistle import Event, EventDispatcher
from enum import Enum
class KernelEvts(Enum):
    MOVEMENT_STOPPED = 0
    SERVERS_LIST = 1
    CHARACTERS_LIST = 2
    CRASH = 3
    LOGGED_IN = 4
    IN_GAME = 5
    DEAD = 6
    ALIVE = 7
        
class KernelEventsManager(EventDispatcher, metaclass=Singleton):
    __waiting_evts = list[threading.Event]()
    def __init__(self):
        super().__init__()
        
    def wait(self, event: KernelEvts, timeout: float = None):
        received = threading.Event()
        ret = [None]
        def onReceived(e, *args, **kwargs):
            received.set()
            ret[0] = kwargs.get('return_value', None) 
        self.once(event, onReceived)
        self.__waiting_evts.append(received)
        received.wait(timeout)
        self.__waiting_evts.remove(received)
        return ret[0]
    
    def on(self, event: KernelEvts, callback):
        self.add_listener(event, callback)
    
    def once(self, event: KernelEvts, callback):
        def onEvt(e):
            self.remove_listener(e, onEvt)
            callback(e)
        self.add_listener(event, onEvt)
    
    def send(self, event_id: KernelEvts, *args, return_value=None, **kwargs):
        if event_id == KernelEvts.CRASH:
            self.stopAllwaiting()
        if event is None:
            event = Event()
        event.dispatcher = self
        event.name = event_id
        if event_id not in self._listeners:
            return event
        for listener in self.get_listeners(event_id):
            listener(event, *args, return_value, **kwargs)
            if event.propagation_stopped: break
    
    def stopAllwaiting(self):
        for evt in self.__waiting_evts:
            evt.set()
        self.__waiting_evts.clear()
