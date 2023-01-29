import threading

lock = threading.RLock()


class ThreadSharedSingleton(type):
    _instances = dict[type, object]()
    _locks = dict[type, threading.RLock]()

    def __call__(cls, *args, **kwargs) -> object:
        with lock:
            if cls not in cls._instances:
                cls._locks[cls] = threading.RLock()
        with cls._locks[cls]:
            if cls not in cls._instances:
                cls._instances[cls] = super(ThreadSharedSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

    def clear(cls):
        with cls._locks[cls]:
            if cls in cls._instances:
                del cls._instances[cls]
