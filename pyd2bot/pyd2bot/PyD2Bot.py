import logging
import sys
import threading
from pyd2bot.thriftServer.pyd2botServer import Pyd2botServer
import pyd2bot.thriftServer.pyd2botService.Pyd2botService as Pyd2botService
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
logger = logging.getLogger(__name__)
class PyD2Bot(metaclass=Singleton):
    _stop = threading.Event()
    _server = None
    
    def runServer(self, host, port):
        self._stop.clear()
        handler = Pyd2botServer()
        processor = Pyd2botService.Processor(handler)
        transport = TSocket.TServerSocket(host=host, port=port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TThreadPoolServer(processor, transport, tfactory, pfactory)
        self._server = server
        print("Server started on {}:{}".format(host, port), flush=True)
        for i in range(server.threads):
            try:
                t = threading.Thread(target=server.serveThread)
                t.setDaemon(server.daemon)
                t.start()
            except Exception as x:
                logger.exception(x)

        # Pump the socket for clients
        server.serverTransport.listen()
        while not self._stop.is_set():
            try:
                client = server.serverTransport.accept()
                if not client:
                    continue
                server.clients.put(client)
            except Exception as x:
                logger.exception(x)
    
    def runClient(self, host, port):
        transport = TSocket.TSocket(host, port)
        transport = TTransport.TBufferedTransport(transport)
        protocol = TBinaryProtocol.TBinaryProtocol(transport)
        client = Pyd2botService.Client(protocol)
        transport.open()
        return transport, client
        
    def stopServer(self):
        self._stop.set()
        print("Server stopped")
        sys.exit(0)