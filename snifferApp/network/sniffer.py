#!/usr/bin/python
import subprocess
from types import FunctionType
import pyshark
import socket
from whistle import Event, EventDispatcher
from com.ankamagames.dofus.network.MessageReceiver import MessageReceiver
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray
from com.ankamagames.jerakine.network.ServerConnection import ServerConnection
from snifferApp.network.message import Message
import threading

logger = Logger("Dofus2")
LOW_LEVEL_DEBUG = False


class SnifferBuffer:
    def __init__(self):
        self.memory = list()
        self.buffer = ByteArray()
        self.nextSeq = None

    def getSeqRw(self, tcp_packet):
        return int(tcp_packet.seq), tcp_packet.payload.binary_value

    def updateFromMemory(self):
        self.memory.sort(key=lambda e: e.seq)
        poped = []
        for packet in self.memory:
            seq, raw = self.getSeqRw(packet)
            if seq == self.nextSeq:
                poped.append(seq)
                self.buffer += raw
                self.nextSeq = seq + len(raw)
        self.memory = [p for p in self.memory if p.seq not in poped]

    def write(self, tcp_packet):
        if LOW_LEVEL_DEBUG:
            logger.debug(f"nextSeq {self.nextSeq}, lenBuffer {len(self.buffer)}, lenMemory {len(self.memory)}")
        seq, data = self.getSeqRw(tcp_packet)
        if LOW_LEVEL_DEBUG:
            logger.debug(f"Write (seq {seq}, len data {len(data)})")
        self.updateFromMemory()
        if self.nextSeq is None or seq == self.nextSeq:
            self.buffer += data
            self.nextSeq = seq + len(data)
        else:
            self.memory.append(tcp_packet)
        self.updateFromMemory()
        if LOW_LEVEL_DEBUG:
            logger.debug(
                f"new next seq {self.nextSeq}, new buffer len {len(self.buffer)}, new memory len {len(self.memory)}"
            )


class ServerMsgHandler:
    def __init__(self, process: FunctionType):
        self.process = process


class PacketEvent(Event):
    def __init__(self, p):
        super().__init__()
        self.packet = p


class Provider(threading.Thread):
    def __init__(self) -> None:
        super().__init__()
        self.killsig = threading.Event()
        self.dispatcher: EventDispatcher = EventDispatcher()
        self.clientBuffer = SnifferBuffer()
        self.serverBuffer = SnifferBuffer()
        self.lastSeq = 0
        self.prevPaLen = 0
        self.LOCAL_IP = self.getLocalIp()
        if LOW_LEVEL_DEBUG:
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
        if LOW_LEVEL_DEBUG:
            logger.debug(f"src: {src}, dst: {dst}, LOCAL_IP: {self.LOCAL_IP}")
        if src == self.LOCAL_IP:
            return True
        elif dst == self.LOCAL_IP:
            return False
        raise Exception(f"Packet origin unknown\nsrc: {src}\ndst: {dst}\nLOCAL_IP: {self.LOCAL_IP}")

    def run(self):
        capture = pyshark.LiveCapture(bpf_filter="tcp port 5555")
        try:
            for p in capture.sniff_continuously():
                if self.killsig.is_set():
                    return True
                try:
                    p.tcp.payload.binary_value
                    if int(p.tcp.seq) == 1:
                        self.reset()
                    isfromClient = self.isFromClient(p)
                    if LOW_LEVEL_DEBUG:
                        logger.debug(f"isfromClient: {isfromClient}")
                    if isfromClient:
                        self.clientBuffer.write(p.tcp)
                        self.dispatcher.dispatch("Client packet received", PacketEvent(p))
                    else:
                        self.serverBuffer.write(p.tcp)
                        self.dispatcher.dispatch("Server packet received", PacketEvent(p))
                except AttributeError as e:
                    # logger.debug(f"AttributeError: {e}", exc_info=True)
                    pass
        except Exception as e:
            logger.error(f"Error: {e}", exc_info=True)

    def interrupt(self):
        self.killsig.set()

    def reset(self):
        self.clientBuffer = SnifferBuffer()
        self.serverBuffer = SnifferBuffer()
        self.lastSeq = 0
        self.prevPaLen = 0


class DofusSniffer:
    def __init__(self, callback):
        self.servConn = ServerConnection()
        self.servConn.rawParser = MessageReceiver()
        self.servConn.handler = ServerMsgHandler(self.processServerMsg)
        self.provider = Provider()
        self.servConn._id = "ServerSniffer"
        self.provider.dispatcher.add_listener("Client packet received", self.onClientPacketReceived, 0)
        self.provider.dispatcher.add_listener("Server packet received", self.onServerPacketReceived, 0)
        self.handle = callback
        self.running = False

    def processServerMsg(self, msg):
        if msg.__class__.__name__ == "SelectedServerDataMessage":
            self.provider.reset()
        self.handle(msg)

    def onClientPacketReceived(self, event: PacketEvent):
        while True:
            msg = Message.fromRaw(
                self.provider.clientBuffer.buffer,
                True,
                src=event.packet.ip.src,
                dst=event.packet.ip.dst,
            )
            if msg:
                self.handle(msg.deserialize(), True)
            else:
                break

    def onServerPacketReceived(self, event: PacketEvent):
        self.servConn.receive(self.provider.serverBuffer.buffer)

    def start(self):
        self.provider.start()
        self.running = True

    def stop(self):
        self.provider.interrupt()
        self.provider.join()
        self.running = False


if __name__ == "__main__":

    def handle(msg):
        pass

    mySniffer = DofusSniffer(handle)
    mySniffer.start()
    subprocess.call("make test bot=shooter", stderr=subprocess.DEVNULL, stdout=subprocess.DEVNULL)
