from pyd2bot.logic.common.frames.BotWorkflowFrame import BotWorkflowFrame
from pyd2bot.thriftServer.pyd2botServer import Pyd2botServer
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.DofusClient import DofusClient
from pyd2bot.logic.managers.SessionManager import SessionManager
import pyd2bot.thriftServer.pyd2botService.Pyd2botService as Pyd2botService
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer

def runSession(sessionId):
    SessionManager().load(sessionId)
    Logger.charachter = SessionManager().charachterId
    dofus2 = DofusClient()
    dofus2.registerFrame(BotWorkflowFrame())
    dofus2.login(SessionManager().loginToken, SessionManager().charachter["serverId"], SessionManager().charachter["charachterId"])
    dofus2.join()


if __name__ == "__main__":
    handler = Pyd2botServer()
    processor = Pyd2botService.Processor(handler)
    transport = TSocket.TServerSocket(host="0.0.0.0", port=9999)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
    server.setNumThreads(5)
    server.serve()
