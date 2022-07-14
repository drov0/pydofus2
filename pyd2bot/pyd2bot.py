import logging
import sys
import threading
from pyd2bot.thriftServer.pyd2botServer import Pyd2botServer
import pyd2bot.thriftServer.pyd2botService.Pyd2botService as Pyd2botService
from thrift.transport import TSocket
from thrift.transport import TTransport
from thrift.protocol import TBinaryProtocol
from thrift.server import TServer
import signal
from thrift.protocol.THeaderProtocol import THeaderProtocolFactory
logger = logging.getLogger(__name__)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--host", help="the server host", type=str, default="0.0.0.0")
    parser.add_argument("--port", help="the server port", type=int, default=9999)
    args = parser.parse_args()
    
    stop = threading.Event()
    handler = Pyd2botServer()
    processor = Pyd2botService.Processor(handler)
    transport = TSocket.TServerSocket(host=args.host, port=args.port)
    tfactory = TTransport.TBufferedTransportFactory()
    pfactory = TBinaryProtocol.TBinaryProtocolFactory()
    server = TServer.TSimpleServer(processor, transport, tfactory, pfactory)
    def handler(signum, frame):
        print('Signal handler called with signal', signum)
        stop.set()
        sys.exit(0)
    signal.signal(signal.SIGINT, handler)
    server.serverTransport.listen()
    print("Server started on {}:{}".format(args.host, args.port), flush=True)
    while not stop.is_set():
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
            while not stop.is_set():
                server.processor.process(iprot, oprot)
        except TTransport.TTransportException:
            pass
        except Exception as x:
            logger.exception(x)

        itrans.close()
        if otrans:
            otrans.close()


    