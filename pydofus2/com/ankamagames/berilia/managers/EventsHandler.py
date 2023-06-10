import threading
from typing import Any, List
from pydofus2.com.ankamagames.berilia.managers.Listener import Listener
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger

lock = threading.RLock()

from queue import PriorityQueue
from typing import Any
from dataclasses import dataclass, field

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Listener=field(compare=False)

class PriorityQueueWithRemove(PriorityQueue):
    def __init__(self):
        super().__init__()
        self.entry_finder = dict[Any, PrioritizedItem]()  # mapping of tasks to entries
        self.counter = 0  # unique sequence count

    def put(self, item: Listener):
        if item in self.entry_finder:
            self.remove(item)
        entry = PrioritizedItem(-item.priority, item)
        self.entry_finder[item] = entry
        super().put(entry)

    def remove(self, item):
        entry: Listener = self.entry_finder.pop(item)
        entry.deleted = True

    def get(self, block=True, timeout=None):
        while True:
            entry: PrioritizedItem = super().get(block, timeout)
            if not entry.item.deleted:
                del self.entry_finder[entry.item]
                return entry.item


class Event(object):
    COMPLETE = "event_complete"
    propagation_stopped = False
    sender: "EventsHandler"
    name: Any
    listener: "Listener"

    def stopPropagation(self):
        self.propagation_stopped = True

class EventsHandler:
    
    def __init__(self):
        super().__init__()
        self._listeners = dict[str, PriorityQueueWithRemove]()
        self._sorted = {}
        self.waitingEvts = list[threading.Event]()
        self._crashMessage = None

    def wait(self, event, timeout: float = None, originator=None):
        received = threading.Event()
        ret = [None]

        def onReceived(e, *args, **kwargs):
            received.set()
            ret[0] = kwargs.get("return_value", None)

        self.once(event, onReceived, originator=originator)
        self.waitingEvts.append(received)
        wait_result = received.wait(timeout)
        if received in self.waitingEvts:
            self.waitingEvts.remove(received)
        if self._crashMessage:
            raise Exception(self._crashMessage)
        if not wait_result:
            raise TimeoutError(f"wait event {event} timed out")
        return ret[0]
    
    def hasListener(self, event_id=None):
        return event_id in self._listeners
    
    def on(
        self,
        event_id,
        callback,
        priority=0,
        timeout=None,
        ontimeout=None,
        once=False,
        originator=None,
        retryNbr=None,
        retryAction=None,
    ):
        if event_id not in self._listeners:
            self._listeners[event_id] =  PriorityQueueWithRemove()
        def onListenerTimeout(listener: Listener):
            if retryNbr:
                listener.nbrTimeouts += 1
                if listener.nbrTimeouts > retryNbr:
                    return ontimeout()
            listener.armTimer()
            if retryAction:
                retryAction()
            elif retryNbr:
                raise Exception("Retry nbr provided but no action to retry!")
        listener = Listener(self, event_id, callback, timeout, onListenerTimeout, once, priority, originator)
        if event_id not in self._listeners:
            Logger().debug(f"Something weird happened, event_id disappeared while installing a listener")
            return
        self._listeners[event_id].put(listener)
        return listener

    def onMultiple(self, listeners, originator=None):
        for event_id, callback in listeners:
            self.on(event_id, callback, originator=originator)

    def once(
        self,
        event_id,
        callback,
        priority=0,
        timeout=None,
        ontimeout=None,
        originator=None,
        retryNbr=None,
        retryAction=None,
    ):
        return self.on(
            event_id,
            callback,
            priority=priority,
            timeout=timeout,
            ontimeout=ontimeout,
            once=True,
            originator=originator,
            retryNbr=retryNbr,
            retryAction=retryAction,
        )

    def getListeners(self, event_id=None) -> List[Listener]:
        if event_id is not None:
            return self._getListenersForEvent(event_id)
        else:
            all_listeners = []
            for event_id in self._listeners:
                all_listeners.extend(self._getListenersForEvent(event_id))
            return all_listeners

    def _getListenersForEvent(self, event_id):
        if event_id in self._listeners:
            temp_queue = PriorityQueueWithRemove()
            listeners = []
            while not self._listeners[event_id].empty():
                listener = self._listeners[event_id].get()
                listeners.append(listener)
                temp_queue.put(listener)
            self._listeners[event_id] = temp_queue
            return listeners
        else:
            return []
        
    def send(self, event_id, *args, **kwargs):
        if event_id not in self._listeners:
            return
        event = Event()
        event.sender = self
        event.name = event_id
        temp_queue = PriorityQueueWithRemove()
        while not self._listeners[event_id].empty():
            listener = self._listeners[event_id].get()
            event = Event()
            event.sender = self
            event.name = event_id
            event.listener = listener
            listener.call(event, *args, **kwargs)
            if listener.once:
                listener.delete()
            else:
                temp_queue.put(listener)
            if event.propagation_stopped:
                break
        self._listeners[event_id] = temp_queue

    def reset(self):
        self.stopAllwaiting()
        for queue in self._listeners.values():
            while not queue.empty():
                queue.get().delete()
        self._listeners.clear()
        Logger().debug("Events manager reseted")

    def stopAllwaiting(self):
        for evt in self.waitingEvts:
            evt.set()
        self.waitingEvts.clear()
        
    def removeListener(self, event_id, callback):
        if event_id not in self._listeners:
            return Logger().warning(f"Event {event_id} not found")
        new_queue = PriorityQueueWithRemove()
        queue = self._listeners[event_id]
        while not queue.empty():
            listener = queue.get()
            if listener.callback != callback:
                new_queue.put(listener)
        self._listeners[event_id] = new_queue

    def getListenersByOrigin(self, origin):
        return [l for l in self.getListeners() if l.origin == origin]

    def clearAllByOrigin(self, origin):
        for event_id, queue in self._listeners.items():
            new_queue = PriorityQueueWithRemove()
            while not queue.empty():
                listener = queue.get()
                if listener.origin != origin:
                    new_queue.put(listener)
                else:
                    listener.delete()
            self._listeners[event_id] = new_queue

