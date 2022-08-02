from threading import Timer
from pyd2bot.logic.roleplay.messages.ExchangeConcludedMessage import ExchangeConcludedMessage
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeAcceptMessage import (
    ExchangeAcceptMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeIsReadyMessage import (
    ExchangeIsReadyMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeLeaveMessage import (
    ExchangeLeaveMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeObjectAddedMessage import (
    ExchangeObjectAddedMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeObjectMoveMessage import (
    ExchangeObjectMoveMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeObjectTransfertAllFromInvMessage import (
    ExchangeObjectTransfertAllFromInvMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeObjectsAddedMessage import ExchangeObjectsAddedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangePlayerRequestMessage import (
    ExchangePlayerRequestMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeReadyMessage import (
    ExchangeReadyMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeRequestedTradeMessage import (
    ExchangeRequestedTradeMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeStartedWithPodsMessage import (
    ExchangeStartedWithPodsMessage,
)
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority
logger = Logger()


class SellerStateEnum:
    IDLE = 4
    GOING_TO_BANK = 1
    INSIDE_BANK = 8
    TREATING_BOT_UNLOAD = 2
    UNLOADING_IN_BANK = 3
    WAITING_FOR_BOT_TO_ARRIVE = 5
    EXCHANGING_WITH_GUEST = 6
    EXCHANGE_REQUEST_SENT = 7
    EXCHANGE_REQUEST_ACCEPTED = 9
    EXCHANGE_ACCEPT_SENT = 10

class BotExchangeFrame(Frame):
    PHENIX_MAPID = None

    def __init__(self, direction: str, target: dict, items: list = None):
        self.direction = direction
        self.target = target
        self.items = items
        if items is None:
            self.giveAll = True
            self.step = 1
        else:
            self.giveAll = False
            self.step = len(items)
        self.wantsToMoveItemToExchange = set()
        self.acceptExchangeTimer : Timer = None
        super().__init__()

    def pushed(self) -> bool:
        logger.debug("BotExchangeFrame pushed")
        if self.direction == "give":
            self.sendExchangeRequest()
        return True

    def pulled(self) -> bool:
        logger.debug("BotExchangeFrame pulled")
        return True

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    def process(self, msg: Message) -> bool:

        if isinstance(msg, ExchangeRequestedTradeMessage):
            if msg.source == self.target["id"]:
                self.state = SellerStateEnum.EXCHANGE_REQUEST_SENT
                ConnectionsHandler.getConnection().send(ExchangeAcceptMessage())

        elif isinstance(msg, ExchangeStartedWithPodsMessage):
            logger.debug("Exchange started.")
            self.state = SellerStateEnum.EXCHANGE_REQUEST_ACCEPTED
            if self.direction == "give":
                if self.giveAll:
                    ConnectionsHandler.getConnection().send(ExchangeObjectTransfertAllFromInvMessage())
                else:
                    for elem in self.items:
                        rmsg = ExchangeObjectMoveMessage()
                        rmsg.init(objectUID_=elem["uid"], quantity_=elem["quantity"])
                        ConnectionsHandler.getConnection().send(rmsg)
                        self.wantsToMoveItemToExchange.add(elem["uid"])
                logger.debug("Moved items to exchange.")
            return True

        elif isinstance(msg, ExchangeObjectsAddedMessage):
            logger.debug("All items moved to exchange.")
            Timer(1, self.sendExchangeReady).start()
                
        elif isinstance(msg, ExchangeObjectAddedMessage):
            logger.debug("Item added to exchange.")
            if self.direction == "give":
                self.wantsToMoveItemToExchange.remove(msg.object.objectUID)
                if len(self.wantsToMoveItemToExchange) == 0:
                    logger.debug("All items moved to exchange.")
                    self.sendExchangeReady()
                    
        elif isinstance(msg, ExchangeIsReadyMessage):
            self.acceptExchangeTimer.cancel()
            logger.debug(f"Exchange is ready received from {msg.id}.")
            if int(msg.id) == int(self.target["id"]):
                self.sendExchangeReady()
                self.state = SellerStateEnum.EXCHANGE_ACCEPT_SENT
                return True

        elif isinstance(msg, ExchangeLeaveMessage):
            logger.debug("ExchangeLeaveMessage received")
            Kernel().getWorker().processImmediately(ExchangeConcludedMessage())
            Kernel().getWorker().removeFrame(self)

    def sendExchangeRequest(self):
        msg = ExchangePlayerRequestMessage()
        msg.init(exchangeType_=1, target_=self.target["id"])
        ConnectionsHandler.getConnection().send(msg)
        self.state = SellerStateEnum.EXCHANGE_REQUEST_SENT
        logger.debug("Exchange open request sent")

    def sendExchangeReady(self):
        readymsg = ExchangeReadyMessage()
        logger.debug(f"Step {self.step}")
        readymsg.init(ready_=True, step_=self.step)
        ConnectionsHandler.getConnection().send(readymsg)
        self.acceptExchangeTimer = Timer(5, self.sendExchangeReady)
        self.acceptExchangeTimer.start()
        self.state = SellerStateEnum.EXCHANGE_ACCEPT_SENT
        logger.debug("Exchange is ready sent.")