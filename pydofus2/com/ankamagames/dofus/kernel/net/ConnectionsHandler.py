import pydofus2.com.ankamagames.dofus.kernel.Kernel as krnl
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionType import ConnectionType
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReason import DisconnectionReason
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import DisconnectionReasonEnum
from pydofus2.com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
from pydofus2.com.ankamagames.dofus.logic.common.utils.LagometerAck import LagometerAck
from pydofus2.com.ankamagames.dofus.logic.connection.frames.HandshakeFrame import HandshakeFrame
from pydofus2.com.ankamagames.dofus.network.MessageReceiver import MessageReceiver
from pydofus2.com.ankamagames.dofus.network.messages.common.basic.BasicPingMessage import BasicPingMessage
from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.ConnectionResumedMessage import ConnectionResumedMessage
from pydofus2.com.ankamagames.jerakine.metaclasses.Singleton import Singleton
from pydofus2.com.ankamagames.jerakine.network.MultiConnection import MultiConnection
from pydofus2.com.ankamagames.jerakine.network.ServerConnection import ServerConnection

logger = Logger("Dofus2")


class ConnectionsHandler(metaclass=Singleton):
    GAME_SERVER: str = "game_server"
    KOLI_SERVER: str = "koli_server"

    def __init__(self):
        self._currentConnection: MultiConnection = None
        self._currentConnectionType: str = None
        self._wantedSocketLost: bool = False
        self._wantedSocketLostReason: int = 0
        self._hasReceivedMsg: bool = False
        self._hasReceivedNetworkMsg: bool = False
        self._connectionTimeout = None
        self._disconnectMessage = ""
        
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

    
    def getConnection(self) -> MultiConnection:
        if not self._currentConnection:
            self.createConnection()
        return self._currentConnection

    
    def connectToLoginServer(self, host: str, port: int) -> None:
        if self._currentConnection != None:
            self.closeConnection()
        self.etablishConnection(host, port, ConnectionType.TO_LOGIN_SERVER)
        self._currentConnectionType = ConnectionType.TO_LOGIN_SERVER

    
    def connectToGameServer(self, gameServerHost: str, gameServerPort: int) -> None:
        self.startConnectionTimer()
        if self._currentConnection != None:
            self.closeConnection()
        self.etablishConnection(
            gameServerHost,
            gameServerPort,
            ConnectionType.TO_GAME_SERVER
        )
        self._currentConnectionType = ConnectionType.TO_GAME_SERVER
        PlayerManager().gameServerPort = gameServerPort

    
    def connectToKoliServer(self, gameServerHost: str, gameServerPort: int) -> None:
        self.startConnectionTimer()
        if self._currentConnection != None and self._currentConnection.getSubConnection(ConnectionType.TO_KOLI_SERVER):
            self._currentConnection.close(ConnectionType.TO_KOLI_SERVER)
        self.etablishConnection(
            gameServerHost,
            gameServerPort,
            ConnectionType.TO_KOLI_SERVER
        )
        self._currentConnectionType = ConnectionType.TO_KOLI_SERVER
        PlayerManager().kisServerPort = gameServerPort

    
    def confirmGameServerConnection(self) -> None:
        self.stopConnectionTimer()

    
    def onConnectionTimeout(self) -> None:
        msg: BasicPingMessage = None
        if self._currentConnection and self._currentConnection.connected:
            msg = BasicPingMessage()
            msg.init(True)
            logger.warn(
                "La connection au serveur de jeu semble longue. On envoit un BasicPingMessage pour essayer de débloquer la situation."
            )
            self._currentConnection.send(msg, self._currentConnectionType)
            self.stopConnectionTimer()

    
    def closeConnection(self) -> None:
        if krnl.Kernel().getWorker().contains("HandshakeFrame"):
            krnl.Kernel().getWorker().removeFrame(krnl.Kernel().getWorker().getFrame("HandshakeFrame"))
        if self._currentConnection and self._currentConnection.connected:
            self._currentConnection.close()
        self._currentConnection = None
        self._currentConnectionType = ConnectionType.DISCONNECTED

    
    def handleDisconnection(self) -> DisconnectionReason:
        self.closeConnection()
        reason: DisconnectionReason = DisconnectionReason(self._wantedSocketLost, self._wantedSocketLostReason, msg=self._disconnectMessage)
        self._wantedSocketLost = False
        self._wantedSocketLostReason = DisconnectionReasonEnum.UNEXPECTED
        return reason

    
    def connectionGonnaBeClosed(self, expectedReason: int, msg: str = "") -> None:
        self._wantedSocketLostReason = expectedReason
        self._wantedSocketLost = True
        self._disconnectMessage = msg

    
    def pause(self) -> None:
        logger.info("Pause connection")
        self._currentConnection.pause()
    
    def resume(self) -> None:
        logger.info("Resume connection")
        if self._currentConnection:
            self._currentConnection.resume()
        krnl.Kernel().getWorker().process(ConnectionResumedMessage())

    
    def startConnectionTimer(self) -> None:
        if self._connectionTimeout:
            self._connectionTimeout.cancel()
        self._connectionTimeout = BenchmarkTimer(4, self.onConnectionTimeout)
        self._connectionTimeout.start()

    
    def stopConnectionTimer(self) -> None:
        if self._connectionTimeout:
            self._connectionTimeout.cancel()

    
    def etablishConnection(
        self,
        host: str,
        port: int,
        id: str
    ) -> None:
        conn = ServerConnection(None, 0, id)
        if self._currentConnection is None:
            self.createConnection()
        conn.lagometer = LagometerAck()
        conn.handler = krnl.Kernel().getWorker()
        conn.rawParser = MessageReceiver()
        self._currentConnection.addConnection(conn, id)
        self._currentConnection.mainConnection = conn
        krnl.Kernel().getWorker().addFrame(HandshakeFrame())
        conn.connect(host, port)

    
    def createConnection(self) -> None:
        self._currentConnection = MultiConnection()
