import socket
import threading
from time import perf_counter, sleep
from whistle import EventDispatcher
from com.ankamagames.jerakine.events.SocketEvent import SocketEvent
from com.ankamagames.jerakine.events.ProgressEvent import ProgressEvent
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.network.CustomDataWrapper import ByteArray

logger = Logger("Dofus2")


class Socket(threading.Thread):
    MIN_TIME_BETWEEN_SEND = 0.0

    def __init__(self, host, port):
        self.dispatcher = EventDispatcher()
        self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connected = False
        self.host = host
        self.port = port
        self._kill = threading.Event()
        self._buff = ByteArray()
        self._lastSent = 0
        super().__init__()

    @property
    def bytesAvailable(self):
        return self._buff.remaining()

    def lenlenData(self, raw):
        if len(raw) > 65535:
            return 3
        if len(raw) > 255:
            return 2
        if len(raw) > 0:
            return 1
        return 0

    def run(self):
        logger.info("Socket thread started.")
        while not self._kill.is_set():
            try:
                rdata = self._sock.recv(1028)
                if rdata:
                    self._buff += rdata
                    self.dispatcher.dispatch(ProgressEvent.SOCKET_DATA, ProgressEvent(rdata))
                else:
                    break
            except OSError as e:
                pass
        self.close()
        logger.info("Socket thread ended")

    def connect(self, host, port):
        self._sock.connect((host, port))
        self.connected = True
        self.started = perf_counter()
        self.start()
        self.dispatcher.dispatch(SocketEvent.CONNECT)

    def close(self):
        if self.connected:
            self.connected = False
            self._kill.set()
            self._sock.close()
            self.dispatchEvent(SocketEvent.CLOSE)

    def addEventListener(self, event, listener, priority=0):
        self.dispatcher.add_listener(event, listener, priority)

    def removeEventListener(self, event, listener):
        self.dispatcher.remove_listener(event, listener)

    def dispatchEvent(self, event):
        self.dispatcher.dispatch(event)

    def send(self, data):
        if self.MIN_TIME_BETWEEN_SEND > 0:
            sleep(max(self.MIN_TIME_BETWEEN_SEND - (perf_counter() - self._lastSent), 0))
        self._sock.sendall(data)
        self._lastSent = perf_counter()
