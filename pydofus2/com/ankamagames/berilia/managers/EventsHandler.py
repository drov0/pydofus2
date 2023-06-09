import operator
import threading
from typing import Any
from pydofus2.com.ankamagames.berilia.managers.Listener import Listener
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger

lock = threading.RLock()

from queue import PriorityQueue
from typing import Any
from dataclasses import dataclass, field

REMOVED = '<removed-task>'

@dataclass(order=True)
class PrioritizedItem:
    priority: int
    item: Any=field(compare=False)

class PriorityQueueWithRemove(PriorityQueue):
    def __init__(self):
        super().__init__()
        self.entry_finder = dict[Any, PrioritizedItem]  # mapping of tasks to entries
        self.counter = 0  # unique sequence count

    def put(self, item, priority=0):
        'Add a new task or update the priority of an existing task'
        if item in self.entry_finder:
            self.remove(item)
        entry = PrioritizedItem(priority, item)
        self.entry_finder[item] = entry
        super().put(entry)

    def remove(self, item):
        'Mark an existing task as REMOVED.  Raise KeyError if not found.'
        entry = self.entry_finder.pop(item)
        entry.item = REMOVED

    def get(self, block=True, timeout=None):
        'Remove and return the lowest priority task. Raise KeyError if empty.'
        while True:
            entry = super().get(block, timeout)
            if entry.item is not REMOVED:
                del self.entry_finder[entry.item]
                return entry.item


class Event(object):
    propagation_stopped = False
    sender: "EventsHandler"
    name: Any
    listener: "Listener"

    def stopPropagation(self):
        self.propagation_stopped = True

class EventsHandler:
    
    def __init__(self):
        super().__init__()
        self._listeners = dict[str, dict[int, list[Listener]]]()
        self._sorted = {}
        self.__waiting_evts = list[threading.Event]()
        self._crashMessage = None

    def wait(self, event, timeout: float = None, originator=None):
        received = threading.Event()
        ret = [None]

        def onReceived(e, *args, **kwargs):
            received.set()
            ret[0] = kwargs.get("return_value", None)

        self.once(event, onReceived, originator=originator)
        self.__waiting_evts.append(received)
        wait_result = received.wait(timeout)
        if received in self.__waiting_evts:
            self.__waiting_evts.remove(received)
        if self._crashMessage:
            raise Exception(self._crashMessage)
        if not wait_result:
            raise TimeoutError(f"wait event {event} timed out")
        return ret[0]
    
    def hasListeners(self, event_id=None):
        return bool(len(self.getSortedListeners(event_id)))
    
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
            self._listeners[event_id] = {}
        if priority not in self._listeners[event_id]:
            self._listeners[event_id][priority] = []

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
            return
        self._listeners[event_id][priority].append(listener)
        if event_id in self._sorted:
            del self._sorted[event_id]
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
            priority,
            timeout,
            ontimeout,
            once=True,
            originator=originator,
            retryNbr=retryNbr,
            retryAction=retryAction,
        )

    def sortListeners(self, event_id):
        self._sorted[event_id] = []
        if event_id in self._listeners:
            self._sorted[event_id] = [
                listener
                for listeners in sorted(self._listeners[event_id].items(), key=operator.itemgetter(0))
                for listener in listeners[1]
            ]

    def getSortedListeners(self, event_id=None) -> list[Listener]:
        if event_id is not None:
            if event_id not in self._sorted:
                self.sortListeners(event_id)
            return self._sorted[event_id]

        for event_id in self._listeners:
            if not event_id in self._sorted:
                self.sortListeners(event_id)
        return list(self.iterListeners())

    def send(self, event_id, *args, **kwargs):
        event = Event()
        event.sender = self
        event.name = event_id
        if not self._listeners.get(event_id):
            return event
        event_listeners = self.getSortedListeners(event_id)
        to_remove = list[Listener]()
        for listener in event_listeners:
            event = Event()
            event.sender = self
            event.name = event_id
            event.listener = listener
            listener.call(event, *args, **kwargs)
            if listener.once:
                to_remove.append(listener)
            if event.propagation_stopped:
                break
            if to_remove:
                with lock:
                    if event_id in self._sorted:
                        del self._sorted[event_id]
                    for listener in to_remove:
                        listener.delete()

    def reset(self):
        self.stopAllwaiting()
        for listener in self.iterListeners():
            listener.delete()
        self._listeners.clear()
        self._sorted.clear()
        Logger().debug("Events manager reseted")

    def iterListeners(self):
        for listenersByPrio in self._listeners.values():
            for listeners in listenersByPrio.values():
                for listener in listeners:
                    yield listener
    
    def stopAllwaiting(self):
        for evt in self.__waiting_evts:
            evt.set()
        self.__waiting_evts.clear()

    def removeListeners(self, event_id, callbacks) -> list:
        if event_id not in self._listeners:
            return Logger().warning(f"Event {event_id} not found")
        for priority, listeners in self._listeners[event_id].items():
            listeners = list(filter(lambda l: l.callback not in callbacks, listeners))
        if event_id in self._sorted:
            del self._sorted[event_id]

    def removeListener(self, event_id, callback):
        if event_id not in self._listeners:
            return Logger().warning(f"Event {event_id} not found")
        for priority, listeners in self._listeners[event_id].items():
            listeners = list(filter(lambda l: l.callback != callback, listeners))
        if event_id in self._sorted:
            del self._sorted[event_id]

    def getListenersByOrigin(self, origin):
        result = list[Listener]()
        for listenersByPrio in self._listeners.values():
            for listeners in listenersByPrio.values():
                for listener in listeners:
                    if listener.origin and listener.origin == origin:
                        result.append(listener)
        return result

    def clearAllByOrigin(self, origin):
        toBeDeleted = self.getListenersByOrigin(origin)
        for listener in toBeDeleted:
            listener.delete()
