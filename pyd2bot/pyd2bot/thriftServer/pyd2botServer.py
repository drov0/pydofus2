from time import perf_counter, sleep
from pydofus2.com.DofusClient import DofusClient
from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
import pyd2bot.thriftServer.pyd2botService.Pyd2botService as Pyd2botService
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
        dofus2 = DofusClient()
        loginToken = Haapi().getLoginToken(login, password, certId, certHash)
        result = list()
        dofus2.login(loginToken)            
        while not PlayerManager().serversList:
            sleep(0.2)
        serversList = PlayerManager().serversList
        print("servers containing charachter : " + str(serversList))
        for serverId in serversList:
            print("logging on server " + str(serverId))
            dofus2._loginToken = Haapi().getLoginToken(login, password, certId, certHash)
            dofus2._serverId = serverId
            dofus2.restart()
            start = perf_counter()
            while not PlayerManager().charactersList:
                sleep(0.2)
                if perf_counter() - start > 10:
                    dofus2.shutdown()
                    raise Exception("timeout")
            for charachter in PlayerManager().charactersList:
                result.append(Charachter(charachter.name, str(charachter.id), str(serverId)))
        print(result)
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