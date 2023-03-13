from enum import Enum
import threading
from typing import List, Tuple, Type, TypeVar
from pydofus2.com.ankamagames.berilia.managers.EventsHandler import Event, EventsHandler
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger

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

    def clear(cls):
        if cls in Singleton._instances[cls.threadName()]:
            del Singleton._instances[cls.threadName()][cls]

    def clearAllChilds(cls):
        scheduledForDelete = []
        for clz in Singleton._instances[cls.threadName()]:
            if isinstance(cls, clz):
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
            # Logger.getInstance(callerThname).debug(f"thread {thid} registred class {clazz.__name__}, waiting for {thname} to register {cls.__name__}")
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
