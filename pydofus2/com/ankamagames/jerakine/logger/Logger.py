import logging
import datetime
import os
from pathlib import Path
import sys
import threading

LOGS_PATH = Path(os.getenv("APPDATA")) / "pydofus2" / "logs"
if not os.path.isdir(LOGS_PATH):
    os.makedirs(LOGS_PATH)


class LoggerSingleton(type):
    _instances = dict[str, object]()

    def __call__(cls, *args, **kwargs) -> object:
        threadName = threading.current_thread().name
        if threadName not in cls._instances:
            cls._instances[threadName] = super(LoggerSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[threadName]

    def clear(cls):
        del cls._instances[threading.current_thread().name]


# this class is a singleton
class Logger(logging.Logger, metaclass=LoggerSingleton):
    def __init__(self, name="DofusLogger"):
        self.name = name
        self.prefix = threading.current_thread().name
        super().__init__(self.prefix)
        self.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(threadName)s|%(asctime)s|%(levelname)s > %(message)s", datefmt="%H:%M:%S")
        now = datetime.datetime.now()
        fileHandler = logging.FileHandler(LOGS_PATH / f"{self.prefix}_{now.strftime('%Y-%m-%d')}.log")
        fileHandler.setFormatter(formatter)
        self.addHandler(fileHandler)
        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setFormatter(formatter)
        self.addHandler(streamHandler)
