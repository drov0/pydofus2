import threading
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger()
class Singleton(type):
    _instances = dict[int, dict[type, object]]()

    def threadName(cls):
        return threading.current_thread().name
    
    def __call__(cls, *args, **kwargs) -> object:
        thrid = cls.threadName()
        if 'pydofus2' not in thrid:
            logger.info("uknown thread of qualname : " + threading.current_thread().__class__.__qualname__)
            logger.warning(f"unknown thread name '{thrid}' asked to register instance of class {cls.__qualname__}!")
        if thrid not in cls._instances:
            logger.info("Wow new thread name: " + thrid)
            cls._instances[thrid] = dict()
        if cls not in cls._instances[thrid]:
            cls._instances[thrid][cls] = super(Singleton, cls).__call__(*args, **kwargs)
            lightobj = {thrid: [c.__qualname__ for c in cls._instances[thrid]] for thrid in cls._instances}
            # logger.debug(f"instances dict: {lightobj}")
        return cls._instances[thrid][cls]

    def clear(cls):
        cls._instances[cls.threadName()].clear()
