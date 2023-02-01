import threading


class Singleton(type):
    THREAD_REGISTER = 0
    _instances = dict[int, dict[type, object]]()
    _listeners = dict[int, list[object]]()

    def threadName(cls):
        return threading.current_thread().name

    @property
    def lightInfo(cls):
        return {thrid: [c.__qualname__ for c in cls._instances[thrid]] for thrid in cls._instances}

    def __call__(cls, *args, **kwargs) -> object:
        thrid = cls.threadName()
        if thrid not in cls._instances:
            cls._instances[thrid] = dict()
        if cls not in cls._instances[thrid]:
            cls._instances[thrid][cls] = super(Singleton, cls).__call__(*args, **kwargs)
            if (
                cls.THREAD_REGISTER in cls._listeners
                and thrid in cls._listeners[cls.THREAD_REGISTER]
                and cls in cls._listeners[cls.THREAD_REGISTER][thrid]
            ):
                for listener in cls._listeners[cls.THREAD_REGISTER][thrid][cls]:
                    listener()
                del cls._listeners[cls.THREAD_REGISTER][thrid][cls]
        return cls._instances[thrid][cls]

    def clear(cls):
        if cls in cls._instances[cls.threadName()]:
            del cls._instances[cls.threadName()][cls]

    def getThreadInstance(cls, thrid: int) -> dict[type, object]:
        if thrid in cls._instances:
            return cls._instances[thrid].get(cls)

    def onceThreadRegister(cls, thname: str, listener: object, *args, **kwargs):
        if cls.THREAD_REGISTER not in cls._listeners:
            cls._listeners[cls.THREAD_REGISTER] = dict()
        if thname not in cls._listeners[cls.THREAD_REGISTER]:
            cls._listeners[cls.THREAD_REGISTER][thname] = {cls: []}
        cls._listeners[cls.THREAD_REGISTER][thname][cls].append(listener)

    def removeListener(cls, thname: str, listener: object):
        if cls.THREAD_REGISTER in cls._listeners and thname in cls._listeners[cls.THREAD_REGISTER]:
            if (
                cls in cls._listeners[cls.THREAD_REGISTER][thname]
                and cls in cls._listeners[cls.THREAD_REGISTER][thname][cls]
                and listener in cls._listeners[cls.THREAD_REGISTER][thname][cls]
            ):
                cls._listeners[cls.THREAD_REGISTER][thname][cls].remove(listener)
