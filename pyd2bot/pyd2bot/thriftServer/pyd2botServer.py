from asyncio.log import logger
from time import perf_counter, sleep
from pyd2bot.thriftServer.pyd2botService.ttypes import Character


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
        logger.info("fetchAccountCharacters called")
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
                    result.append(Character(character.name, str(character.id), str(server.id)))
            else:
                logger.debug(f"Server {server.id} not online but has status {ServerStatusEnum(server.status).name}.")
        dofus2.shutdown()
        return result
        
    def runSession(self, login:str, password:str, certId:str, certHash:str, sessionId:str) -> None:
        pass
