from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from time import perf_counter
from pydofus2.com.DofusClient import DofusClient
from pydofus2.com.ankamagames.dofus import Constants
import pydofus2.com.ankamagames.dofus.kernel.Kernel as krnl
import pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler as connh
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import (
    DisconnectionReasonEnum,
)
from pydofus2.com.ankamagames.dofus.logic.connection.managers.AuthentificationManager import AuthentificationManager
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.managers.StoreDataManager import StoreDataManager
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.messages.WrongSocketClosureReasonMessage import (
    WrongSocketClosureReasonMessage,
)
from pydofus2.com.ankamagames.jerakine.network.ServerConnectionClosedMessage import (
    ServerConnectionClosedMessage,
)
from pydofus2.com.ankamagames.jerakine.network.messages.ExpectedSocketClosureMessage import (
    ExpectedSocketClosureMessage,
)
from pydofus2.com.ankamagames.jerakine.network.messages.UnexpectedSocketClosureMessage import (
    UnexpectedSocketClosureMessage,
)
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority
import pydofus2.com.ankamagames.dofus.logic.game.approach.frames.GameServerApproachFrame as gsaF

logger = Logger("Dofus2")


class DisconnectionHandlerFrame(Frame):

    CONNECTION_ATTEMPTS_NUMBER: int = 4

    messagesAfterReset: list = list()

    _connectionUnexpectedFailureTimes: list

    _numberOfAttemptsAlreadyDone: int = 0

    _timer: BenchmarkTimer

    _mustShowLoginInterface: bool = False

    def __init__(self):
        self._connectionUnexpectedFailureTimes = list()
        self._timer = None
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.LOW

    def resetConnectionAttempts(self) -> None:
        self._connectionUnexpectedFailureTimes = list()
        StoreDataManager().setData(Constants.DATASTORE_MODULE_DEBUG, "connection_fail_times", None)
        self._numberOfAttemptsAlreadyDone = 0

    def pushed(self) -> bool:
        logger.debug("DisconnectionHandlerFrame pushed")
        return True

    def handleUnexpectedNoMsgReceived(self):
        self._numberOfAttemptsAlreadyDone += 1
        logger.warn(
            f"The connection was closed unexpectedly. Reconnection attempt {self._numberOfAttemptsAlreadyDone}/{self.CONNECTION_ATTEMPTS_NUMBER} will start in 4s."
        )
        self._connectionUnexpectedFailureTimes.append(perf_counter())
        StoreDataManager().setData(
            Constants.DATASTORE_MODULE_DEBUG,
            "connection_fail_times",
            self._connectionUnexpectedFailureTimes,
        )
        self._timer = BenchmarkTimer(4, self.reconnect)
        self._timer.start()

    def process(self, msg: Message) -> bool:

        if isinstance(msg, ServerConnectionClosedMessage):
            logger.debug("Server Connection Closed.")
            sccmsg = msg
            if (
                connh.ConnectionsHandler.getConnection()
                and connh.ConnectionsHandler.getConnection().mainConnection
                and (
                    connh.ConnectionsHandler.getConnection().mainConnection.connected
                    or connh.ConnectionsHandler.getConnection().mainConnection.connecting
                )
            ):
                logger.debug("The connection was closed before we even receive any message. Will halt.")
                return False

            logger.debug("The connection was closed. Checking reasons.")
            gsaF.GameServerApproachFrame.authenticationTicketAccepted = False
            reason = connh.ConnectionsHandler.handleDisconnection()
            if connh.ConnectionsHandler.hasReceivedMsg:
                if (
                    not reason.expected and
                    not connh.ConnectionsHandler.hasReceivedNetworkMsg
                    and self._numberOfAttemptsAlreadyDone < self.CONNECTION_ATTEMPTS_NUMBER
                ):
                    self.handleUnexpectedNoMsgReceived()
                else:
                    if not reason.expected:
                        logger.debug(f"The connection was closed unexpectedly. Reseting.")
                        self._connectionUnexpectedFailureTimes.append(perf_counter())
                        StoreDataManager().setData(
                            Constants.DATASTORE_MODULE_DEBUG,
                            "connection_fail_times",
                            self._connectionUnexpectedFailureTimes,
                        )
                        if self._timer:
                            self._timer.cancel()
                        self._timer = BenchmarkTimer(7, self.reconnect)
                        self._timer.start()
                    else:
                        logger.debug(
                            f"The connection closure was expected (reason: {reason.reason})."
                        )
                        if (
                            reason.reason == DisconnectionReasonEnum.DISCONNECTED_BY_POPUP
                            or reason.reason == DisconnectionReasonEnum.SWITCHING_TO_HUMAN_VENDOR
                            or reason.reason == DisconnectionReasonEnum.WANTED_SHUTDOWN
                        ):
                            krnl.Kernel().reset()
                        elif reason.reason == DisconnectionReasonEnum.RESTARTING:
                            self.reconnect()
                        else:
                            krnl.Kernel().getWorker().process(ExpectedSocketClosureMessage(reason.reason))
            else:
                logger.warn("The connection hasn't even start.")
            return True

        elif isinstance(msg, WrongSocketClosureReasonMessage):
            wscrmsg = msg
            gsaF.GameServerApproachFrame.authenticationTicketAccepted = False
            logger.error(
                "Expecting socket closure for reason "
                + str(wscrmsg.expectedReason)
                + ", got reason "
                + str(wscrmsg.gotReason)
                + "! Reseting."
            )
            krnl.Kernel().reset([UnexpectedSocketClosureMessage()])
            return True

        elif isinstance(msg, UnexpectedSocketClosureMessage):
            logger.debug("go hook UnexpectedSocketClosure")
            gsaF.GameServerApproachFrame.authenticationTicketAccepted = False
            return True

    def reconnect(self) -> None:
        logger.debug("Reconnecting...")
        krnl.Kernel().reset(reloadData=True, autoRetry=True)
        DofusClient().relogin()

    def pulled(self) -> bool:
        return True
