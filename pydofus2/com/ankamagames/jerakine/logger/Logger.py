import logging
import datetime
import os
from pathlib import Path
import threading

LOGS_PATH = Path(os.getenv("APPDATA")) / "pydofus2" / "logs"
if not os.path.isdir(LOGS_PATH):
    os.makedirs(LOGS_PATH)
from typing import Type, TypeVar
T = TypeVar("T")
class LoggerSingleton(type):
    _instances = dict[str, object]()

    def __call__(cls, *args, **kwargs) -> object:
        threadName = threading.current_thread().name
        if threadName not in LoggerSingleton._instances:
            LoggerSingleton._instances[threadName] = super(LoggerSingleton, cls).__call__(*args, **kwargs)
        return LoggerSingleton._instances[threadName]

    def clear(cls):
        del LoggerSingleton._instances[threading.current_thread().name]
    
    def getInstance(cls: Type[T], thname: int) -> T:
        return LoggerSingleton._instances.get(thname)

class Logger(logging.Logger, metaclass=LoggerSingleton):
    
    def __init__(self, name="DofusLogger", consoleOut=True):
        self.name = name
        self.prefix = threading.current_thread().name
        super().__init__(self.prefix)
        self.setLevel(logging.DEBUG)
        formatter = logging.Formatter(
            "%(filename)s|%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s", datefmt="%H:%M:%S"
        )
        now = datetime.datetime.now()
        fileHandler = logging.FileHandler(LOGS_PATH / f"{self.prefix}_{now.strftime('%Y-%m-%d')}.log")
        fileHandler.setFormatter(formatter)
        self.addHandler(fileHandler)
        # if consoleOut:
        #     streamHandler = logging.StreamHandler(sys.stdout)
        #     streamHandler.setFormatter(formatter)
        #     self.addHandler(streamHandler)
    
    def separator(self, msg, separator="="):
        format_row = "\n{:<50} {:^30} {:>70}\n"
        text = format_row.format(separator * 50, msg, separator * 70)
        self.info(text)
