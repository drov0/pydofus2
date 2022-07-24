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
import signal
from thrift.protocol.THeaderProtocol import THeaderProtocolFactory
logger = logging.getLogger(__name__)

class PyD2Bot(metaclass=Singleton):
    _stop = threading.Event()
    
    def run(self, host, port):
        self._stop.clear()
        handler = Pyd2botServer()
        processor = Pyd2botService.Processor(handler)
        transport = TSocket.TServerSocket(host=host, port=port)
        tfactory = TTransport.TBufferedTransportFactory()
        pfactory = TBinaryProtocol.TBinaryProtocolFactory()
        server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
        def handler(signum, frame):
            print('Signal handler called with signal', signum)
            self._stop.set()
            sys.exit(0)
        signal.signal(signal.SIGINT, handler)
        server.serverTransport.listen()
        print("Server started on {}:{}".format(host, port), flush=True)
        while not self._stop.is_set():
            client = server.serverTransport.accept()
            if not client:
                continue

            itrans = server.inputTransportFactory.getTransport(client)
            iprot = server.inputProtocolFactory.getProtocol(itrans)

            # for THeaderProtocol, we must use the same protocol instance for
            # input and output so that the response is in the same dialect that
            # the server detected the request was in.
            if isinstance(server.inputProtocolFactory, THeaderProtocolFactory):
                otrans = None
                oprot = iprot
            else:
                otrans = server.outputTransportFactory.getTransport(client)
                oprot = server.outputProtocolFactory.getProtocol(otrans)

            try:
                while not self._stop.is_set():
                    server.processor.process(iprot, oprot)
            except TTransport.TTransportException:
                pass
            except Exception as x:
                print("Exception occured : ", x)
                logger.exception(x)

            itrans.close()
            if otrans:
                otrans.close()
        print("Server stopped")
        return 0

    def stop(self):
        self._stop.set()
        print("Server stopped")
        sys.exit(0)