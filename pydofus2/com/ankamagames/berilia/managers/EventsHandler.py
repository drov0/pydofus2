import operator
import threading
from datetime import timedelta
from typing import Any

from whistle import EventDispatcher

from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import \
    BenchmarkTimer
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger

lock = threading.RLock()


class Event(object):
    propagation_stopped = False
    sender: "EventsHandler"
    name: Any
    listener: "Listener"

    def stop_propagation(self):
        self.propagation_stopped = True


class Listener:
    def __init__(
        self,
        manager: "EventsHandler",
        event_id,
        callback: callable,
        timeout=None,
        ontimeout=None,
        once=False,
        priority=0,
        originator=None,
    ):
        self._deleted = False
        self.event_id = event_id
        self.callback = callback
        self.timeout = timeout
        self.timeoutCallback = ontimeout
        self.timeoutTimer = None
        if timeout:
            self.armTimer()
        self.once = once
        self.priority = priority
        self.manager = manager
        self.thname = threading.current_thread().name
        self.originator = originator
        self.nbrTimeouts = 0

    def call(self, event: Event, *args, **kwargs):
        if self._deleted:
            return Logger().warning("Callback called of a deleted listener")
        self.cancelTimer()
        self.callback(event, *args, **kwargs)

    def delete(self):
        self._deleted = True
        self.cancelTimer()
        if self.event_id not in self.manager._listeners:
            return Logger().warning("Trying to delete Event not registred")
        listeners = self.manager._listeners[self.event_id][self.priority]
        if self in listeners:
            listeners.remove(self)
            if self.event_id in self.manager._sorted:
                del self.manager._sorted[self.event_id]

    def armTimer(self, newTimeout=None):
        if self._deleted:
            return Logger().warning("arm timer of a deleted listener")
        if newTimeout:
            self.timeout = newTimeout
        self.timeoutTimer = BenchmarkTimer(self.timeout, lambda: self.timeoutCallback(self))
        self.timeoutTimer.start()

    def cancelTimer(self):
        if self.timeoutTimer:
            self.timeoutTimer.cancel()

    def __str__(self):
        summary = f"Listener(event_id={self.event_id}, priority={self.priority}, callback={self.callback.__name__}, "
        if self.timeoutTimer and not self.timeoutTimer.finished.is_set():
            remaining_time = self.timeoutTimer.remainingTime()
            summary += f"timeout={self.timeout}, time_left={remaining_time})"
        else:
            summary += f"timeout={self.timeout})"
        return summary


class EventsHandler(EventDispatcher):
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

    def sort_listeners(self, event_id):
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
                self.sort_listeners(event_id)
            return self._sorted[event_id]

        for event_id in self._listeners:
            if not event_id in self._sorted:
                self.sort_listeners(event_id)

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

    def iterListeners(self):
        for listenersByPrio in self._listeners.values():
            for listeners in listenersByPrio.values():
                for listener in listeners:
                    yield listener

    def stopAllwaiting(self):
        for evt in self.__waiting_evts:
            evt.set()
        self.__waiting_evts.clear()

    def remove_listeners(self, event_id, callbacks) -> list:
        if event_id not in self._listeners:
            return Logger().warning(f"Event {event_id} not found")
        for priority, listeners in self._listeners[event_id].items():
            listeners = list(filter(lambda l: l.callback not in callbacks, listeners))
        if event_id in self._sorted:
            del self._sorted[event_id]

    def remove_listener(self, event_id, callback):
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
                    if listener.originator and listener.originator == origin:
                        result.append(listener)
        return result

    def clearAllByOrigin(self, origin):
        toBeDeleted = self.getListenersByOrigin(origin)
        for listener in toBeDeleted:
            listener.delete()
