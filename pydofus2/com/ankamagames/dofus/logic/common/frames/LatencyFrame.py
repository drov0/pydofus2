from datetime import datetime
from time import perf_counter
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.network.messages.common.basic.BasicPongMessage import (
    BasicPongMessage,
)
from com.ankamagames.dofus.network.messages.game.basic.BasicLatencyStatsMessage import (
    BasicLatencyStatsMessage,
)
from com.ankamagames.dofus.network.messages.game.basic.BasicLatencyStatsRequestMessage import (
    BasicLatencyStatsRequestMessage,
)
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.network.IServerConnection import IServerConnection
from com.ankamagames.jerakine.types.enums.Priority import Priority

logger = Logger(__name__)


class LatencyFrame(Frame):

    pingRequested: int = 0

    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.NORMAL

    def pushed(self) -> bool:
        return True

    def process(self, msg: Message) -> bool:
        bpmsg: BasicPongMessage = None
        pongReceived: int = 0
        delay: int = 0
        blsrmsg: BasicLatencyStatsRequestMessage = None
        connection: IServerConnection = None
        blsmsg: BasicLatencyStatsMessage = None
        if isinstance(msg, BasicPongMessage):
            bpmsg = msg
            if bpmsg.quiet:
                return True
            pongReceived = perf_counter()
            delay = pongReceived - self.pingRequested
            self.pingRequested = 0
            msg = f'[LatencyMeter] Pong {delay}ms ! {datetime.now().strftime("%H:%M:%S")}'
            logger.debug(msg)
            return True
        elif isinstance(msg, BasicLatencyStatsRequestMessage):
            blsrmsg = msg
            connection = ConnectionsHandler.getConnection().getSubConnection(blsrmsg.sourceConnection)
            blsmsg = BasicLatencyStatsMessage()
            blsmsg.init(
                min(32767, int(connection.latencyAvg)),
                connection.latencySamplesCount,
                connection.latencySamplesMax,
            )
            ConnectionsHandler.getConnection().send(blsmsg, blsrmsg.sourceConnection)
            return True
        else:
            return False

    def pulled(self) -> bool:
        return True
