from asyncio.log import logger
import json
import logging
from time import perf_counter, sleep


from pyd2bot.thriftServer.pyd2botService.ttypes import Character, Spell

logger = None


class Pyd2botServer:
    def __init__(self):
        pass
    
    def fetchAccountCharacters(self, login:str, password:str, certId:str, certHash:str) -> list[Character]:
        from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
        Logger.prefix = login
        from pydofus2.com.ankamagames.haapi.Haapi import Haapi
        from pydofus2.com.DofusClient import DofusClient
        from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
        from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
        from pydofus2.com.ankamagames.dofus.logic.connection.frames.ServerSelectionFrame import ServerSelectionFrame
        from pydofus2.com.ankamagames.dofus.network.enums.ServerStatusEnum import ServerStatusEnum
        logging.info("fetchAccountCharacters called")
        rate = 2.
        timeout = 10.
        loginToken = Haapi().getLoginToken(login, password, certId, certHash)
        result = list()
        dofus2 = DofusClient()
        dofus2.login(loginToken)
        start = perf_counter()
        while not PlayerManager().serversList:
            sleep(1/rate)
            if perf_counter() - start > timeout:
                raise TimeoutError("timeout")
        start = perf_counter()
        ssf = None
        while True:
            ssf : 'ServerSelectionFrame' = Kernel().getWorker().getFrame('ServerSelectionFrame')
            if ssf:
                break
            sleep(1/rate)
            if perf_counter() - start > timeout:
                raise TimeoutError("timeout")
        usedServers = ssf._serversUsedList.copy()
        for server in usedServers:
            if ServerStatusEnum(server.status) == ServerStatusEnum.ONLINE or ServerStatusEnum(server.status) == ServerStatusEnum.NOJOIN:
                dofus2._loginToken = Haapi().getLoginToken(login, password, certId, certHash)
                dofus2._serverId = server.id
                dofus2.restart()
                start = perf_counter()
                while not PlayerManager().charactersList:
                    sleep(1/rate)
                    if perf_counter() - start > timeout:
                        raise TimeoutError("timeout")
                for character in PlayerManager().charactersList:
                    chkwrgs = {
                        "name": character.name, 
                        "id": character.id, 
                        "level": character.level, 
                        "breedId": character.breedId, 
                        "breedName": character.breed.name, 
                        "serverId": server.id, 
                        "serverName": PlayerManager().server.name
                    }
                    result.append(Character(**chkwrgs))
            else:
                logging.debug(f"Server {server.id} not online but has status {ServerStatusEnum(server.status).name}.")
        dofus2.shutdown()
        return result
        
    def runSession(self, login:str, password:str, certId:str, certHash:str, sessionJson:str) -> None:
        from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
        print(f"runSession called with login {login}")
        session = json.loads(sessionJson)
        logger_name = f"{session['character']['name']}({session['character']['id']})"
        Logger.prefix = logger_name
        logger = Logger()
        logger.debug(f"logger_name {logger_name}")
        logger.debug("session: " + sessionJson)
        from pyd2bot.logic.managers.SessionManager import SessionManager
        SessionManager().load(sessionJson)
        logger.debug("Session loaded")
        from pydofus2.com.ankamagames.haapi.Haapi import Haapi
        from pydofus2.com.DofusClient import DofusClient
        dofus2 = DofusClient()
        logger.debug("importing frames")
        from pyd2bot.logic.common.frames.BotCharacterUpdatesFrame import BotCharacterUpdatesFrame
        from pyd2bot.logic.common.frames.BotWorkflowFrame import BotWorkflowFrame
        from pyd2bot.logic.roleplay.frames.BotPartyFrame import BotPartyFrame
        logger.debug("frames imported")
        dofus2.registerInitFrame(BotWorkflowFrame)
        dofus2.registerGameStartFrame(BotCharacterUpdatesFrame)
        logger.debug("registerGameStartFrame BotCharacterUpdatesFrame")
        dofus2.registerGameStartFrame(BotPartyFrame)
        logger.debug("registerGameStartFrame BotPartyFrame")
        logger.debug("Frames registered")
        if session.get("APIKEY"):
            Haapi().APIKEY = session["APIKEY"]
        loginToken = Haapi().getLoginToken(login, password, certId, certHash)
        if loginToken is None:
            raise Exception("Unable to generate login token.")
        logger.debug(f"loginToken: {loginToken}")
        dofus2.login(loginToken, SessionManager().character["serverId"], SessionManager().character["id"])
        try:
            dofus2.join()
        except Exception as e:
            logger.error(f"Error while running session: {e}")
            from pyd2bot.PyD2Bot import PyD2Bot
            PyD2Bot().stopServer()
        
    def fetchBreedSpells(self, breedId:int) -> list['Spell']:
        from pydofus2.com.ankamagames.dofus.datacenter.breeds.Breed import Breed
        spells = []
        breed = Breed.getBreedById(breedId)
        if not breed:
            raise Exception(f"Breed {breedId} not found.")
        for spellVariant in breed.breedSpellVariants:
            for spellBreed in spellVariant.spells:
                spells.append(Spell(spellBreed.id, spellBreed.name))
        return spells
    
    def fetchJobsInfosJson(self) -> str:
        import json
        from pydofus2.com.ankamagames.dofus.datacenter.jobs.Skill import Skill
        res = {}
        skills = Skill.getSkills()
        for skill in skills:
            if skill.gatheredRessource:
                if skill.parentJobId not in res:
                    res[skill.parentJobId] = { 
                        "id" : skill.parentJobId,
                        "name": skill.parentJob.name,
                        "gatheredRessources": [] 
                    }
                gr = {"name": skill.gatheredRessource.name, "id": skill.gatheredRessource.id, "levelMin": skill.levelMin}
                if gr not in res[skill.parentJobId]["gatheredRessources"]:
                    res[skill.parentJobId]["gatheredRessources"].append(gr)
        return json.dumps(res)
    
    def getApiKey(self, login:str, password:str, certId:str, certHash:str) -> str:
        from pydofus2.com.ankamagames.haapi.Haapi import Haapi
        response = Haapi().createAPIKEY(login, password, certId, certHash, game_id=102)
        return json.dumps(response)

    def moveToVertex(self, vertex: str):
        from pyd2bot.logic.roleplay.messages.LeaderPosMessage import LeaderPosMessage
        from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
        from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Vertex import Vertex
        v = Vertex(**json.loads(vertex))
        Kernel().getWorker().process(LeaderPosMessage(v))
        print("LeaderPosMessage processed")
        
    def followTransition(self, transition: str):        
        from pyd2bot.logic.roleplay.messages.LeaderTransitionMessage import LeaderTransitionMessage
        from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
        from pydofus2.com.ankamagames.dofus.modules.utils.pathFinding.world.Transition import Transition
        tr = Transition(**json.loads(transition))
        Kernel().getWorker().process(LeaderTransitionMessage(tr))
        print("LeaderTransitionMessage processed")