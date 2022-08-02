import json
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pyd2bot.logic.managers.PathManager import PathManager
from pydofus2.com.ankamagames.haapi.Haapi import Haapi
logger = Logger()



class SessionManager(metaclass=Singleton):
    character = None
    path = None
    isLeader: bool = None
    leader = None
    followers: list[str] = None
    jobIds = None
    resourceIds = None

    def __init__(self) -> None:
        pass
    
    def generateLoginToken(self, login, password, certId, certHash):
        self.loginToken = Haapi().getLoginToken(login, password, certId, certHash)
        
    def load(self, sessionstr: str):
        sessionJson = json.loads(sessionstr)
        self.type = sessionJson.get("type")
        self.character = sessionJson.get("character")
        self.unloadType = sessionJson.get("unloadType")
        self.seller = sessionJson.get("seller")
        if self.type == "farm":
            self.path = sessionJson.get("path")
            self.jobIds = sessionJson.get("jobIds")
            self.resourceIds = sessionJson.get("resourceIds")
        elif self.type == "fight":
            self.followers : list[str] = sessionJson.get("followers")
            self.party = True
            if self.followers is not None:
                self.isLeader = True
                self.path = sessionJson.get("path")
                logger.info(f"Running path {self.path}")
            else:
                self.isLeader = False
                self.leader : int = sessionJson.get("leader")
        if self.path:
            self.path = PathManager.from_json(sessionJson["path"])
