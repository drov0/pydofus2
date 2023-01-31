import threading
from whistle import Event, EventDispatcher
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger

lock = threading.Lock()
class EventsHandler(EventDispatcher):

    def __init__(self):
        super().__init__()
        self._listeners = {}
        self._sorted = {}
        self.__waiting_evts = list[threading.Event]()
        self._crashMessage = None

    def wait(self, event, timeout: float = None):
        received = threading.Event()
        ret = [None]
        def onReceived(e, *args, **kwargs):
            received.set()
            ret[0] = kwargs.get("return_value", None)
        self.once(event, onReceived)
        self.__waiting_evts.append(received)
        received.wait(timeout)
        if received in self.__waiting_evts:
            self.__waiting_evts.remove(received)
        elif self._crashMessage:
            raise Exception(self._crashMessage)
        return ret[0]

    def on(self, event_id, listener, priority=0):
        with lock:
            if event_id not in self._listeners:
                self._listeners[event_id] = {}
                
            if priority not in self._listeners[event_id]:
                self._listeners[event_id][priority] = []
            self._listeners[event_id][priority].append(listener)
            
            if event_id in self._sorted:
                del self._sorted[event_id]
        
    def once(self, event, callback):
        def onEvt(e, *args, **kwargs):
            self.remove_listener(event, onEvt)
            callback(e, *args, **kwargs)
        self.on(event, onEvt)

    def send(self, event_id, *args, **kwargs):
        event = Event()
        event.sender = self
        event.name = event_id
        if not self._listeners.get(event_id):
            return event
        event_listeners = self.get_listeners(event_id)
        for listener in event_listeners:
            listener(event, *args, **kwargs)
            if event.propagation_stopped:
                break

    def reset(self):
        self.stopAllwaiting()
        self._listeners.clear()

    def stopAllwaiting(self):
        for evt in self.__waiting_evts:
            evt.set()
        self.__waiting_evts.clear()
