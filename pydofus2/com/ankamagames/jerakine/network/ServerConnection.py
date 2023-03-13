import errno
import functools
import queue
import socket
import sys
import threading as mp
import traceback
from time import perf_counter
from typing import TYPE_CHECKING

from pydofus2.com.ankamagames.dofus.network.MessageReceiver import MessageReceiver
from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.ConnectedMessage import ConnectedMessage
from pydofus2.com.ankamagames.jerakine.messages.ConnectionProcessCrashedMessage import ConnectionProcessCrashedMessage
from pydofus2.com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray
from pydofus2.com.ankamagames.jerakine.network.LagometerAck import LagometerAck
from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.jerakine.network.INetworkMessage import INetworkMessage


def sendTrace(func):
    @functools.wraps(func)
    def wrapped(self: "ServerConnection", *args, **kwargs):
        try:
            return func(self, *args, **kwargs)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            traceback_in_var = traceback.format_tb(exc_traceback)
            error_trace = str(e) + '\n' + str(exc_type) + "\n" + str(exc_value) + "\n" + "\n".join(traceback_in_var)
            self._put(ConnectionProcessCrashedMessage(error_trace))

    return wrapped


class ServerConnection(mp.Thread):

    DEBUG_VERBOSE: bool = False
    LOG_ENCODED_CLIENT_MESSAGES: bool = False
    DEBUG_LOW_LEVEL_VERBOSE: bool = False
    DEBUG_DATA: bool = False
    LATENCY_AVG_BUFFER_SIZE: int = 50
    MESSAGE_SIZE_ASYNC_THRESHOLD: int = 300 * 1024
    CONNECTION_TIMEOUT = 7

    def __init__(self, id: str = "ServerConnection", receptionQueue: queue.Queue = None):
        super().__init__(name=mp.current_thread().name)
        self.id = id
        self._latencyBuffer = []
        self._remoteSrvHost = None
        self._remoteSrvPort = None

        self._connecting = mp.Event()
        self._connected = mp.Event()
        self._closing = mp.Event()
        self._paused = mp.Event()
        self.finished = mp.Event()

        self.__packet_id = None
        self.__msg_len_len = None
        self.__msg_len = None

        self.__receivedStream = ByteArray()
        self.__pauseQueue = list["INetworkMessage"]()
        self.__sendingQueue = list["INetworkMessage"]()

        self._sendSequenceId: int = 0
        self._latestSent: int = 0
        self._lastSent: int = None

        self._firstConnectionTry: bool = True
        if receptionQueue is None:
            self.__receptionQueue = queue.Queue(200)
        else:
            self.__receptionQueue = receptionQueue
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.__connectionTimeout = None

    @property
    def latencyAvg(self) -> int:
        if len(self._latencyBuffer) == 0:
            return 0
        total: int = 0
        for latency in self._latencyBuffer:
            total += latency
        return int(total / len(self._latencyBuffer))

    @property
    def latencySamplesCount(self) -> int:
        return len(self._latencyBuffer)

    @property
    def latencySamplesMax(self) -> int:
        return self.LATENCY_AVG_BUFFER_SIZE

    @property
    def port(self) -> int:
        return self._remoteSrvPort

    @property
    def host(self) -> int:
        return self._remoteSrvHost

    @property
    def lastSent(self) -> int:
        return self._lastSent

    @property
    def sendSequenceId(self) -> int:
        return self._sendSequenceId

    @property
    def open(self) -> bool:
        return self._connected.is_set()

    @property
    def connecting(self) -> bool:
        return self._connecting.is_set()

    @property
    def paused(self) -> bool:
        return self._paused.is_set()

    def _put(self, msg):
        if not self._paused.is_set():
            self.__receptionQueue.put(msg)
        else:
            self.__pauseQueue.append(msg)

    @sendTrace
    def close(self) -> None:
        if self.closed or self.finished.is_set():
            Logger().warn(f"[{self.id}] Tried to close a socket while it had already been disconnected.")
            return
        Logger().debug(f"[{self.id}] Closing connection...")
        self.__socket.close()
        self.__sendingQueue.clear()
        self._closing.set()

    @sendTrace
    def send(self, msg: "INetworkMessage") -> None:
        if not self.open:
            if self.connecting:
                self.__sendingQueue.append(msg)
            return Logger().warning(f"Message {msg} was queued")
        Logger().debug(f"[{self.id}] [SND] > {msg}")
        try:
            data = msg.pack()
            total_sent = 0
            while total_sent < len(data):
                sent = self.__socket.send(data[total_sent:])
                if sent == 0:
                    raise RuntimeError("Socket connection broken")
                total_sent += sent
        except OSError as e:
            Logger().debug(f"[SND]{e.errno}, {errno.errorcode[e.errno]} OS error received")
        self._latestSent = perf_counter()
        self._lastSent = perf_counter()
        self._sendSequenceId += 1

    def pause(self) -> None:
        self._paused.set()

    @sendTrace
    def resume(self) -> None:
        self._paused.clear()
        while self.__pauseQueue and not self.paused:
            msg = self.__pauseQueue.pop(0)
            if self.DEBUG_DATA:
                Logger().debug(f"[{self.id}] [RCV] (after Resume) {msg}")
            self.__receptionQueue.put(msg)

    def __parse(self):
        buffer = self.__receivedStream
        while buffer.remaining() and not self._closing.is_set():
            if self.__msg_len_len is None:
                if buffer.remaining() < 2:
                    break
                staticHeader = buffer.readUnsignedShort()
                self.__packet_id = staticHeader >> NetworkMessage.BIT_RIGHT_SHIFT_LEN_PACKET_ID
                self.__msg_len_len = staticHeader & NetworkMessage.BIT_MASK
            if self.__msg_len is None:
                if buffer.remaining() < self.__msg_len_len:
                    break
                self.__msg_len = int.from_bytes(buffer.read(self.__msg_len_len), "big")
            if buffer.remaining() < self.__msg_len:
                break
            self.updateLatency()
            msg: NetworkMessage = MessageReceiver().parse(buffer, self.__packet_id, self.__msg_len)
            if msg.unpacked:
                msg.receptionTime = perf_counter()
                msg.sourceConnection = self.id
                self._put(msg)
            self.__packet_id = None
            self.__msg_len_len = None
            self.__msg_len = None
        buffer.trim()

    @sendTrace
    def updateLatency(self) -> None:
        if self._paused.is_set() or len(self.__pauseQueue) > 0 or self._latestSent == 0:
            return
        packetReceived: int = perf_counter()
        latency: int = packetReceived - self._latestSent
        self._latestSent = 0
        self._latencyBuffer.append(latency)
        if len(self._latencyBuffer) > self.LATENCY_AVG_BUFFER_SIZE:
            self._latencyBuffer.pop(0)

    def stopConnectionTimeout(self) -> None:
        if self.__connectionTimeout:
            self.__connectionTimeout.cancel()

    def __onConnect(self) -> None:
        Logger().debug(f"[{self.id}] Connection established.")
        self.stopConnectionTimeout()
        self._connecting.clear()
        self._connected.set()
        for msg in self.__sendingQueue:
            self.send(msg)
        self.__receivedStream = ByteArray()
        self.__receptionQueue.put(ConnectedMessage())

    @sendTrace
    def receive(self) -> "INetworkMessage":
        return self.__receptionQueue.get()

    def __onClose(self, err) -> None:
        self.stopConnectionTimeout()
        Logger().debug(f"[{self.id}] Connection closed. {err}")
        self.__socket.close()
        self._connected.clear()
        from pydofus2.com.ankamagames.jerakine.network.ServerConnectionClosedMessage import (
            ServerConnectionClosedMessage,
        )

        self.__receptionQueue.put(ServerConnectionClosedMessage(self.id))
        self.finished.set()
        Logger().info(f"[{self.id}] Finished.")
        if err:
            raise err

    @property
    def closed(self) -> bool:
        return self._closing.is_set()

    def __onConnectionTimeout(self) -> None:
        from pydofus2.com.ankamagames.jerakine.network.messages.ServerConnectionFailedMessage import (
            ServerConnectionFailedMessage,
        )

        self.stopConnectionTimeout()
        if self._connected.is_set() or self.finished.is_set() or self._closing.is_set():
            return
        self._connecting.clear()
        if self._firstConnectionTry:
            Logger().debug(f"[{self.id}] Connection timeout, but WWJD ? Give a second chance !")
            self._firstConnectionTry = False
            self.connect(self._remoteSrvHost, self._remoteSrvPort)
        else:
            self.__receptionQueue.put(ServerConnectionFailedMessage(self.id, "Connection timeout!"))

    @sendTrace
    def connect(self, host: str, port: int, timeout=CONNECTION_TIMEOUT) -> None:
        if self.connecting:
            Logger().warn(f"[{self.id}] Tried to connect while already connecting.")
            return
        self._connected.clear()
        self._connecting.set()
        self._closing.clear()
        self._firstConnectionTry = True
        self._remoteSrvHost = host
        self._remoteSrvPort = port
        Logger().info(f"[{self.id}] Connecting to {host}:{port}...")
        # self.__connectionTimeout = BenchmarkTimer(timeout, self.__onConnectionTimeout)
        # self.__connectionTimeout.start()
        self.__socket.connect((host, port))

    @sendTrace
    def run(self):
        err = ""
        while not self._closing.is_set() and not self.finished.is_set():
            try:
                rdata = self.__socket.recv(2056)
                if rdata:
                    if self._connecting.is_set():
                        self.__onConnect()
                    self.__receivedStream += rdata
                    self.__parse()
                else:
                    Logger().debug(f"[{self.id}] Connection closed by remote host")
                    self._closing.set()
            except (KeyboardInterrupt, SystemExit) as e:
                Logger().debug(f"[{self.id}] Interrupted suddenly!")
                self._closing.set()
                err = e
            except OSError as e:
                if e.errno == errno.WSAENOTCONN:
                    Logger().debug(f"[{self.id}] Waiting for socket to connect...")
                    self._closing.wait(0.5)
                elif e.errno == errno.WSAECONNABORTED:
                    Logger().debug(f"[{self.id}] Connection aborted by user.")
                    self._closing.set()
                elif e.errno == errno.WSAECONNRESET:
                    Logger().debug(f"[{self.id}] Connection reset by peer.")
                    self._closing.set()
                elif e.errno == errno.WSAENOTSOCK:
                    Logger().debug(f"[{self.id}] Socket apears to be closed.")
                    if not self._closing.is_set():
                        err = e
                        self._closing.set()
                # elif e.errno == errno.WSAETIMEDOUT:
                #     Logger().debug(f"[{self.id}] Connection timed out.")
                else:
                    Logger().debug(f"{e.errno}, {errno.errorcode[e.errno]} OS error received")
                    err = e
                    self._closing.set()
        self.__onClose(err)
