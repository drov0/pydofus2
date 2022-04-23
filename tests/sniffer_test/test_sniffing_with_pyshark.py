#!/usr/bin/python
from pickletools import int4
import subprocess
import pyshark
import socket

from whistle import Event, EventDispatcher
from com.ankamagames.dofus.network.MessageReceiver import MessageReceiver
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray
from com.ankamagames.jerakine.network.ServerConnection import ServerConnection
from snifferApp.network.message import Message
from threading import Thread

logger = Logger(__name__)


class ServMsgHandler:
    def process(self, msg: Message):
        pass


class PacketEvent(Event):
    def __init__(self, p):
        super().__init__()
        self.packet = p


class Provider(Thread):

    LOW_LEVEL_DEBUG = False

    def __init__(self) -> None:
        super().__init__()
        self.dispatcher: EventDispatcher = EventDispatcher()
        self.clientBuffer = ByteArray()
        self.serverBuffer = ByteArray()
        self.LOCAL_IP = self.getLocalIp()
        logger.debug(f"LOCAL_IP: {self.LOCAL_IP}")

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
        if self.LOW_LEVEL_DEBUG:
            logger.debug(f"src: {src}, dst: {dst}, LOCAL_IP: {self.LOCAL_IP}")
        if src == self.LOCAL_IP:
            return True
        elif dst == self.LOCAL_IP:
            return False
        raise Exception(
            f"Packet origin unknown\nsrc: {src}\ndst: {dst}\nLOCAL_IP: {self.LOCAL_IP}"
        )

    def run(self):
        capture = pyshark.LiveCapture(
            interface="Ethernet 4", bpf_filter="tcp port 5555"
        )
        for p in capture.sniff_continuously():
            try:
                isfromClient = self.isFromClient(p)
                if self.LOW_LEVEL_DEBUG:
                    logger.debug(f"isfromClient: {isfromClient}")
                raw = p.tcp.payload.binary_value
                if isfromClient:
                    self.clientBuffer += raw
                    self.dispatcher.dispatch("Client packet received", PacketEvent(p))
                else:
                    self.serverBuffer += raw
                    self.dispatcher.dispatch("Server packet received", PacketEvent(p))
            except AttributeError as e:
                pass


class DofusSniffer:
    def __init__(self, action):
        self.servConn = ServerConnection()
        self.servConn.rawParser = MessageReceiver()
        self.servConn.handler = ServMsgHandler()
        self.provider = Provider()
        self.servConn._id = "ServerSniffer"
        self.provider.dispatcher.add_listener(
            "Client packet received", self.onClientPacketReceived, 0
        )
        self.provider.dispatcher.add_listener(
            "Server packet received", self.onServerPacketReceived, 0
        )
        self.handle = action

    def mockReceiveFromServer(self, raw):
        self.fromServerBuffer += raw
        logger.info(
            f"[{self.servConn._id}] Receive Event, byte available : {self.fromServerBuffer.remaining()}"
        )
        self.servConn.receive(self.fromServerBuffer)

    def onClientPacketReceived(self, event: PacketEvent):
        while True:
            msg = Message.fromRaw(
                self.provider.clientBuffer,
                True,
                src=event.packet.ip.src,
                dst=event.packet.ip.dst,
            )
            if not msg:
                self.provider.clientBuffer.position = 0
                break
            del self.provider.clientBuffer[: self.provider.clientBuffer.position]
            self.provider.clientBuffer.position = 0
            self.handle(msg)

    def onServerPacketReceived(self, event: PacketEvent):
        self.servConn.receive(self.provider.serverBuffer)

    def start(self):
        self.provider.start()


if __name__ == "__main__":

    def handle(msgRaw: Message):
        msg = msgRaw.deserialize()
        if msgRaw.from_client:
            logger.debug("[Client] [SND] the msg" + str(msg))

    mySniffer = DofusSniffer(handle)
    mySniffer.start()
    subprocess.call(
        "make test bot=shooter", stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL
    )
