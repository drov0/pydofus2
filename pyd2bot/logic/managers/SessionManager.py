import json
import os

from pyd2bot.BotConstants import BotConstants
from pyd2bot.models.Session import Session

SESSIONDB = BotConstants.PERSISTENCE_DIR / "sessions.json"


class SessionManager:
    if not os.path.exists(SESSIONDB):
        with open(SESSIONDB, "w") as fp:
            json.dump({}, fp)
    with open(SESSIONDB, "r") as fp:
        _db = json.load(fp)

    @classmethod
    def getSession(cls, sessionId: str):
        sessionJson = cls._db.get(sessionId)
        return Session(**sessionJson)
