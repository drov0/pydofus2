import logging
import datetime
import os
from pathlib import Path
import sys
import threading

LOGS_PATH = Path(os.getenv("APPDATA")) / "pydofus2" / "logs"
if not os.path.isdir(LOGS_PATH):
    os.makedirs(LOGS_PATH)
class ThreadLogFilter(logging.Filter):
    """
    This filter only show log entries for specified thread name
    """

    def __init__(self, thread_name, *args, **kwargs):
        logging.Filter.__init__(self, *args, **kwargs)
        self.thread_name = thread_name

    def filter(self, record):
        return record.threadName == self.thread_name
    
class LoggerSingleton(type):
    _instances = dict[int, dict[type, object]]()
    
    def __call__(cls, *args, **kwargs) -> object:
        thrid = threading.current_thread().name
        if thrid not in cls._instances:
            cls._instances[thrid] = dict()
        if cls not in cls._instances[thrid]:
            cls._instances[thrid][cls] = super(LoggerSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[thrid][cls]

    def clear(cls):
        cls._instances[threading.current_thread().name].clear()

# this class is a singleton
class Logger(logging.Logger, metaclass=LoggerSingleton):
    
    def __init__(self, log_prefix=""):
        super().__init__("logger")
        self.setLevel(logging.DEBUG)
        self.prefix = threading.current_thread().name
        formatter = logging.Formatter("%(threadName)s|%(asctime)s|%(levelname)s|%(filename)s:%(lineno)s | %(message)s", datefmt='%H:%M:%S')
        now = datetime.datetime.now()
            
        fileHandler = logging.FileHandler(
            LOGS_PATH / f"{self.prefix}_{now.strftime('%Y-%m-%d')}.log"
        )
        fileHandler.setFormatter(formatter)
        self.addHandler(fileHandler)
        
        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setFormatter(formatter)
        self.addHandler(streamHandler)
        self._instance = self
    
    def packArgs(self, *args, **kwargs):
        strargs = ', '.join([str(arg) for arg in args])
        strkwargs = ', '.join([f"{key}={value}" for key, value in kwargs.items()])
        return f"{strargs}, {strkwargs}"

    def get_logger(self):
        return self
