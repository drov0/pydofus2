import json
import os
import threading
from time import perf_counter, sleep
from pydofus2.com.DofusClient import DofusClient
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pyd2bot.BotConstants import BotConstants
from pyd2bot.logic.managers.CharactersManager import CharactersManager
from pyd2bot.logic.managers.PathManager import PathManager
from pydofus2.com.ankamagames.haapi.Haapi import Haapi

SESSIONDB = BotConstants.PERSISTENCE_DIR / "sessions.json"
logger = Logger("Dofus2")


class SessionMonitor(threading.Thread):
    def __init__(self):
        super().__init__()

    def run(self) -> None:
        while True:
            if perf_counter() - SessionManager().lastFightTime > 60 * 2.5:
                SessionManager().lastFightTime = perf_counter()
                DofusClient().restart()
            sleep(15)


class SessionManager(metaclass=Singleton):
    characterId: str = None
    creds: dict = None
    spellId: int = None
    pathId: int = None
    statToUp: int = None
    isLeader: bool = None
    followers: list[str] = None
    leaderName: str = None
    lastFightTime = 0

    def __init__(self) -> None:
        pass
    
    def generateLoginToken(self, login, password, certId, certHash):
        self.loginToken = Haapi().getLoginToken(login, password, certId, certHash)
        
    def load(self, sessionstr: str):
        sessionJson = json.loads(sessionstr)
        self.characterId : str = sessionJson.get("characterId")
        self.character : str = sessionJson.get("character")
        self.spellId : str = sessionJson.get("spellId")
        self.pathId : str = sessionJson.get("pathId")
        self.statToUp: int = sessionJson.get("statToUp")
        self.isLeader: bool = sessionJson.get("isLeader")
        logger.debug(f"is leader {self.isLeader}")
        self.followers: list[str] = sessionJson.get("followers")
        self.leaderName: str = sessionJson.get("leaderName")
        if self.isLeader is not None:
            if "path" not in sessionJson:
                raise ValueError("A leader must have a definded path")
            self.path = PathManager.from_json(sessionJson["path"])
            if self.followers is None:
                logger.warn("No followers for leader")
        else:
            if not self.leaderName:
                raise Exception("Must provide a leader name for a follower")
        self.isSolo = self.isLeader is None and self.followers is None
        self.monitor = SessionMonitor()
        self.monitor.start()
