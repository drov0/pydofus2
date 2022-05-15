import json
import os
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pyd2bot.BotConstants import BotConstants
from pyd2bot.logic.managers.BotCredsManager import BotCredsManager
from pyd2bot.logic.managers.PathManager import PathManager

SESSIONDB = BotConstants.PERSISTENCE_DIR / "sessions.json"
logger = Logger("Dofus2")


class SessionManager(metaclass=Singleton):
    if not os.path.exists(SESSIONDB):
        with open(SESSIONDB, "w") as fp:
            json.dump({}, fp)
    with open(SESSIONDB, "r") as fp:
        _db = json.load(fp)
    charachterId: str = None
    creds: dict = None
    spellId: int = None
    pathId: int = None
    statToUp: int = None
    isLeader: bool = None
    followers: list[str] = None
    leaderName: str = None

    def __init__(self) -> None:
        pass

    def load(self, sessionId: str):
        sessionJson = self._db.get(sessionId)
        if not sessionJson:
            raise ValueError(f"No session with id {sessionId}")
        self.charachterId = sessionJson.get("charachterId")
        self.creds = BotCredsManager.getEntry(str(self.charachterId))
        self.spellId = sessionJson.get("spellId")
        self.pathId = sessionJson.get("charachterId")
        self.statToUp: int = sessionJson.get("statToUp")
        self.isLeader: bool = sessionJson.get("isLeader")
        logger.debug(f"is leader {self.isLeader}")
        self.followers: list[str] = sessionJson.get("followers")
        self.leaderName: str = sessionJson.get("leaderName")

        if self.isLeader is not None:
            if not self.pathId:
                raise ValueError("A leader must have a definded path")
            self.path = PathManager.getPath(str(sessionJson.get("pathId")))
            if self.followers is None:
                logger.warn("No followers for leader")
        else:
            if not self.leaderName:
                raise Exception("Must provide a leader name for a follower")

        self.isSolo = self.isLeader is None and self.followers is None
