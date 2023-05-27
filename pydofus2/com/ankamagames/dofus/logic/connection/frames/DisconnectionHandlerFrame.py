from time import perf_counter

import pydofus2.com.ankamagames.dofus.logic.game.approach.frames.GameServerApproachFrame as gsaF
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import (
    KernelEvent, KernelEventsManager)
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
    ConnectionsHandler
from pydofus2.com.ankamagames.dofus.kernel.net.DisconnectionReasonEnum import \
    DisconnectionReasonEnum as Reason
from pydofus2.com.ankamagames.jerakine.benchmark.BenchmarkTimer import \
    BenchmarkTimer
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.ConnectionProcessCrashedMessage import \
    ConnectionProcessCrashedMessage
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.messages.WrongSocketClosureReasonMessage import \
    WrongSocketClosureReasonMessage
from pydofus2.com.ankamagames.jerakine.network.messages.ExpectedSocketClosureMessage import \
    ExpectedSocketClosureMessage
from pydofus2.com.ankamagames.jerakine.network.messages.UnexpectedSocketClosureMessage import \
    UnexpectedSocketClosureMessage
from pydofus2.com.ankamagames.jerakine.network.ServerConnectionClosedMessage import \
    ServerConnectionClosedMessage
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority


class DisconnectionHandlerFrame(Frame):
    
    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.LOW

    def pushed(self) -> bool:
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, ServerConnectionClosedMessage):
            KernelEventsManager().send(KernelEvent.CONNECTION_CLOSED, msg.closedConnection)
            return True

        elif isinstance(msg, WrongSocketClosureReasonMessage):
            wscrmsg = msg
            Logger().error(
                "Expecting socket closure for reason "
                + str(wscrmsg.expectedReason)
                + ", got reason "
                + str(wscrmsg.gotReason)
                + "! Reseting."
            )
            Kernel().reset([UnexpectedSocketClosureMessage()])
            return True

        elif isinstance(msg, UnexpectedSocketClosureMessage):
            Logger().debug("Got hook UnexpectedSocketClosure")
            KernelEventsManager().send(KernelEvent.CRASH, message="Unexpected socket closure")
            return True

        elif isinstance(msg, ConnectionProcessCrashedMessage):
            Logger().debug("Connection process crashed with error : " + msg.err)
            KernelEventsManager().send(KernelEvent.CRASH, message=msg.err)
            return True

    def pulled(self) -> bool:
        return True
