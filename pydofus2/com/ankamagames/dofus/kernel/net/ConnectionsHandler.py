import queue
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionType import ConnectionType
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReason import DisconnectionReason
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import DisconnectionReasonEnum
from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
from pydofus2.com.ankamagames.dofus.logic.connection.frames.HandshakeFrame import HandshakeFrame
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.ConnectionResumedMessage import ConnectionResumedMessage
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.network.INetworkMessage import INetworkMessage
from pydofus2.com.ankamagames.jerakine.network.ServerConnection import ServerConnection


class ConnectionsHandler(metaclass=Singleton):

    GAME_SERVER: str = "game_server"
    KOLI_SERVER: str = "koli_server"
    CONNECTION_TIMEOUT: int = 3

    def __init__(self):
        self._conn: ServerConnection = None
        self._currentConnectionType: str = None
        self._wantedSocketLost: bool = False
        self._wantedSocketLostReason: int = 0
        self._hasReceivedMsg: bool = False
        self._hasReceivedNetworkMsg: bool = False
        self._disconnectMessage = ""
        self._receivedMsgsQueue = queue.Queue()

    @property
    def connectionType(self) -> str:
        return self._currentConnectionType

    @property
    def hasReceivedMsg(self) -> bool:
        return self._hasReceivedMsg

    @hasReceivedMsg.setter
    def hasReceivedMsg(self, value: bool) -> None:
        self._hasReceivedMsg = value

    @property
    def hasReceivedNetworkMsg(self) -> bool:
        return self._hasReceivedNetworkMsg

    @hasReceivedNetworkMsg.setter
    def hasReceivedNetworkMsg(self, value: bool) -> None:
        self._hasReceivedNetworkMsg = value

    @property
    def conn(self) -> ServerConnection:
        return self._conn

    def connectToLoginServer(self, host: str, port: int) -> None:
        self.etablishConnection(host, port, ConnectionType.TO_LOGIN_SERVER)
        self._currentConnectionType = ConnectionType.TO_LOGIN_SERVER

    def connectToGameServer(self, host: str, port: int) -> None:
        self.etablishConnection(host, port, ConnectionType.TO_GAME_SERVER)
        self._currentConnectionType = ConnectionType.TO_GAME_SERVER
        PlayerManager().gameServerPort = port

    def restart(self) -> None:
        self.closeConnection(DisconnectionReasonEnum.RESTARTING)

    def handleDisconnection(self) -> DisconnectionReason:
        reason: DisconnectionReason = DisconnectionReason(
            self._wantedSocketLost, self._wantedSocketLostReason, self._disconnectMessage
        )
        self._wantedSocketLost = False
        self._wantedSocketLostReason = DisconnectionReasonEnum.UNEXPECTED
        self._disconnectMessage = ""
        return reason

    def closeConnection(self, reason: DisconnectionReasonEnum, message: str = ""):
        Logger().debug(f"[ConnHandler] Close connection : {reason.name}, {message}")
        self._wantedSocketLostReason = reason
        self._wantedSocketLost = True
        self._disconnectMessage = message
        Kernel().worker.removeFrameByName("HandshakeFrame")
        if self._conn.open:
            self._conn.close()
            self._conn.join()
        self._currentConnectionType = ConnectionType.DISCONNECTED

    def etablishConnection(self, host: str, port: int, id: str) -> None:
        self._conn = ServerConnection(id, self._receivedMsgsQueue)
        Kernel().worker.addFrame(HandshakeFrame())
        self._conn.start()
        self._conn.connect(host, port)

    def receive(self) -> INetworkMessage:
        return self._receivedMsgsQueue.get()

    def putMessage(self, msg: INetworkMessage) -> None:
        self._receivedMsgsQueue.put(msg)