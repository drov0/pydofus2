import logging
import datetime
import os
import pydofus2.com.ankamagames.dofus.Constants as Constants

class Logger(logging.Logger):
    _logger = None

    def __init__(self, log_prefix=""):
        super().__init__("logger")
        self._prefix = log_prefix
        self.setLevel(logging.DEBUG)
        formatter = logging.Formatter("%(asctime)s [%(levelname)s | %(filename)s:%(lineno)s] > %(message)s")
        now = datetime.datetime.now()
        if not os.path.isdir(Constants.LOGS_PATH):
            os.mkdir(Constants.LOGS_PATH)
        fileHandler = logging.FileHandler(
            Constants.LOGS_PATH / f"/{self._prefix}_{os.getpid()}_{now.strftime('%Y-%m-%d')}.log"
        )
        streamHandler = logging.StreamHandler()
        fileHandler.setFormatter(formatter)
        streamHandler.setFormatter(formatter)
        self.addHandler(fileHandler)
        self.addHandler(streamHandler)

    def get_logger(self):
        return self
