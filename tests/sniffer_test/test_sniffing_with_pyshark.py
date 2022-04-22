#!/usr/bin/python
import signal
import subprocess
import pyshark
import socket
from com.ankamagames.dofus.network.MessageReceiver import MessageReceiver
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.network.CustomDataWrapper import Buffer, ByteArray
from com.ankamagames.jerakine.network.ServerConnection import ServerConnection
from snifferApp.network.message import Message
from threading import Thread

logger = Logger(__name__)


class ServMsgHandler:
    def process(self, msg: Message):
        pass


class DofusSniffer(Thread):
    def __init__(self, action):

        self.LOCAL_IP = self.getLocalIp()
        self.AUTH_SERVER_IP = None
        self.fromClientBuffer = Buffer()
        self.fromServerBuffer = ByteArray()
        self.servConn = ServerConnection()
        self.servConn.rawParser = MessageReceiver()
        self.servConn.handler = ServMsgHandler()
        self.servConn._id = "ServerSniffer"

    def getLocalIp(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(("10.255.255.255", 1))
            local_ip = s.getsockname()[0]
        except:
            local_ip = "127.0.0.1"
        finally:
            s.close()
        return local_ip

    def isFromClient(self, pa):
        dst = pa.ip.dst
        src = pa.ip.src
        if src == self.LOCAL_IP:
            return True
        elif dst == self.LOCAL_IP:
            return False
        raise Exception(
            f"Packet origin unknown\nsrc: {src}\ndst: {dst}\nLOCAL_IP: {self.LOCAL_IP}"
        )

    def mockReceiveFromServer(self, raw):
        self.fromServerBuffer += raw
        logger.info(
            f"[{self.servConn._id}] Receive Event, byte available : {self.fromServerBuffer.remaining()}"
        )
        self.servConn.receive(self.fromServerBuffer)

    def start(self):
        capture = pyshark.LiveCapture(bpf_filter="tcp port 5555")
        capture.set_debug()
        for p in capture.sniff_continuously():
            try:
                dst = p.ip.dst
                src = p.ip.src
                isfromClient = self.isFromClient(p)
                raw = p.tcp.payload.binary_value
                if isfromClient:
                    self.fromClientBuffer += raw
                    while True:
                        msg = Message.fromRaw(
                            self.fromClientBuffer,
                            isfromClient,
                            src=src,
                            dst=dst,
                        )
                        if not msg:
                            self.fromClientBuffer.position = 0
                            break
                        handle(msg)
                else:
                    self.fromServerBuffer += raw
                    logger.info(
                        f"[{self.servConn._id}] Receive Event, byte available : {self.fromServerBuffer.remaining()}"
                    )
                    self.servConn.receive(self.fromServerBuffer)
            except AttributeError as e:
                pass


if __name__ == "__main__":

    def handle(msgRaw: Message):
        msg = msgRaw.deserialize()
        if msgRaw.from_client:
            print(">>>>>>>>>>>> " + str(msg))

    mySniffer = DofusSniffer(handle)
    mySniffer.start()
    signal.signal(signal.SIGINT, mySniffer.stop)
    subprocess.call(
        "make test bot=shooter", stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
    )
