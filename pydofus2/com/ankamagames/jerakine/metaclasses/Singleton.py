import threading
from enum import Enum
from typing import List, Tuple, Type, TypeVar

from pydofus2.com.ankamagames.berilia.managers.EventsHandler import (
    Event, EventsHandler)
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger

LOCK = threading.Lock()
T = TypeVar("T")

class SingletonEvent(Enum):
    THREAD_REGISTER = 0
class Singleton(type):
    THREAD_REGISTER = 0
    _instances = dict[int, dict[type, object]]()
    eventsHandler = EventsHandler()

    def threadName(cls):
        return threading.current_thread().name

    @property
    def lightInfo(cls):
        return {thrid: [c.__qualname__ for c in cls._instances[thrid]] for thrid in cls._instances}

    def __call__(cls, *args, **kwargs) -> object:
        thrid = cls.threadName()
        if thrid not in Singleton._instances:
            Singleton._instances[thrid] = dict()
        if cls not in cls._instances[thrid]:
            Singleton._instances[thrid][cls] = super(Singleton, cls).__call__(*args, **kwargs)
            Singleton.eventsHandler.send(SingletonEvent.THREAD_REGISTER, thrid, cls)
        return Singleton._instances[thrid][cls]

    @staticmethod
    def clearAll():
        thrid = threading.current_thread().name
        Singleton._instances[thrid].clear()

    def clear(cls):
        with LOCK:
            if cls in Singleton._instances[cls.threadName()]:
                del Singleton._instances[cls.threadName()][cls]
        Logger().debug(f"{cls.__name__} reseted")

    def getSubs(cls: Type[T], thname=None) -> list[T]:
        thname = thname if thname is not None else cls.threadName()
        for clz in Singleton._instances[thname]:
            if issubclass(clz, cls):
                yield Singleton._instances[thname][clz]
    
    def clearAllChilds(cls):
        with LOCK:
            scheduledForDelete = []
            for clz in Singleton._instances[cls.threadName()]:
                if issubclass(clz, cls):
                    scheduledForDelete.append(clz)
            for clz in scheduledForDelete:
                Logger().debug(f"{clz.__name__} singleton instance cleared")
                del Singleton._instances[cls.threadName()][clz]
            scheduledForDelete.clear()

    def getInstance(cls: Type[T], thrid: int) -> T:
        if thrid in Singleton._instances:
            return Singleton._instances[thrid].get(cls)

    def getInstances(cls: Type[T]) -> List[Tuple[str, T]]:
        return [(thd, Singleton._instances[thd][cls]) for thd in Singleton._instances if cls in Singleton._instances[thd]]
    
    def onceThreadRegister(cls, thname: str, listener: object, args=[], kwargs={}, priority=0, timeout=None, ontimeout=None):
        callerThname = cls.threadName()
        if thname in Singleton._instances and cls in Singleton._instances[thname]:
            return listener(*args, **kwargs)
        def onThreadRegister(evt: Event, thid, clazz):
            if thid == thname and clazz.__name__ == cls.__name__:
                Logger.getInstance(callerThname).info(f"{thid} registred class {clazz.__name__}")
                evt.listener.delete()
                listener(*args, **kwargs)
        Singleton.eventsHandler.on(SingletonEvent.THREAD_REGISTER, onThreadRegister, priority, timeout, ontimeout)

    def WaitThreadRegister(cls, thname: int, timeout: float):
        if thname in Singleton._instances and cls in Singleton._instances[thname]:
            return True
        waitEvt = threading.Event()
        cls.onceThreadRegister(thname, waitEvt.set)
        if not waitEvt.wait(timeout):
            raise TimeoutError(f"wait for {cls.__name__} signleton instanciation from thread {thname} timed out!")
