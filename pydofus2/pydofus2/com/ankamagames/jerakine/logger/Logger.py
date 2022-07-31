import logging
import datetime
import os
import sys

from anyio import Path
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton

class Logger(logging.Logger, metaclass=Singleton):
    _logger = None
    prefix = None
    LOGS_PATH = Path(os.getenv("APPDATA")) / "pydofus2" / "logs"
    def __init__(self, log_prefix=""):
        super().__init__("logger")
        self.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(message)s", datefmt='%H:%M:%S')
        now = datetime.datetime.now()
        if not os.path.isdir(self.LOGS_PATH):
            os.mkdir(self.LOGS_PATH)
        fileHandler = logging.FileHandler(
            self.LOGS_PATH / f"{self.prefix}_{now.strftime('%Y-%m-%d')}.log"
        )
        fileHandler.setFormatter(formatter)
        self.addHandler(fileHandler)
        
        streamHandler = logging.StreamHandler(sys.stdout)
        streamHandler.setFormatter(formatter)
        self.addHandler(streamHandler)

    def get_logger(self):
        return self
