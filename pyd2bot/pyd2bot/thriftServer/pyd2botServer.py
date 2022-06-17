from asyncio.log import logger
from time import perf_counter, sleep
from pydofus2.com.DofusClient import DofusClient
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
import pyd2bot.thriftServer.pyd2botService.Pyd2botService as Pyd2botService
from pydofus2.com.ankamagames.dofus.logic.connection.frames.ServerSelectionFrame import ServerSelectionFrame
from pydofus2.com.ankamagames.dofus.network.enums.ServerStatusEnum import ServerStatusEnum
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
from pydofus2.com.ankamagames.haapi.Haapi import Haapi
from pyd2bot.thriftServer.pyd2botService.ttypes import Charachter

class Pyd2botServer:
    def __init__(self):
        pass
    
    def fetchAccountCharachters(self, login:str, password:str, certId:str, certHash:str) -> list[Charachter]:
        logger.info("fetchAccountCharachters called")
        dofus2 = DofusClient()
        loginToken = Haapi().getLoginToken(login, password, certId, certHash)
        result = list()
        dofus2.login(loginToken)
        ssf = None
        start = perf_counter()          
        while not PlayerManager().serversList:
            sleep(1)
            if perf_counter() - start > 10:
                dofus2.shutdown()
                raise Exception("timeout")
        while not ssf:
            sleep(1)
            if perf_counter() - start > 10:
                dofus2.shutdown()
                raise Exception("timeout")
            ssf : 'ServerSelectionFrame' = Kernel().getWorker().getFrame("ServerSelectionFrame")
        usedServers = ssf._serversUsedList.copy()
        for server in usedServers:
            if ServerStatusEnum(server.status) == ServerStatusEnum.ONLINE or ServerStatusEnum(server.status) == ServerStatusEnum.NOJOIN:
                dofus2._loginToken = Haapi().getLoginToken(login, password, certId, certHash)
                dofus2._serverId = server.id
                dofus2.restart()
                start = perf_counter()
                while not PlayerManager().charactersList:
                    sleep(1)
                    if perf_counter() - start > 10:
                        dofus2.shutdown()
                        raise Exception("timeout")
                for charachter in PlayerManager().charactersList:
                    result.append(Charachter(charachter.name, str(charachter.id), str(server.id)))
            else:
                logger.debug(f"Server {server.id} not online but has status {ServerStatusEnum(server.status).name}.")
        dofus2.shutdown()
        return result
        
    def runSession(self, login:str, password:str, certId:str, certHash:str, sessionId:str) -> None:
        pass

if __name__ == '__main__':
    handler = Pyd2botServer()
    processor = Pyd2botService.Processor(handler)
    transport = TSocket.TServerSocket(host="0.0.0.0", port=9999)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
    server.setNumThreads(5)
    server.serve()