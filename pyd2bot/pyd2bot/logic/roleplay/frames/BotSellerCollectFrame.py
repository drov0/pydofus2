from pyd2bot.logic.roleplay.frames.BotBankInteractionFrame import BotBankInteractionFrame
from pyd2bot.logic.roleplay.messages.BankInteractionEndedMessage import BankInteractionEndedMessage
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeAcceptMessage import ExchangeAcceptMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeIsReadyMessage import ExchangeIsReadyMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeLeaveMessage import ExchangeLeaveMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangePlayerRequestMessage import ExchangePlayerRequestMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeReadyMessage import ExchangeReadyMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeRequestedTradeMessage import ExchangeRequestedTradeMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeStartedWithPodsMessage import ExchangeStartedWithPodsMessage
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority
from pyd2bot.logic.roleplay.frames.BotAutoTripFrame import BotAutoTripFrame
from pyd2bot.logic.roleplay.messages.AutoTripEndedMessage import AutoTripEndedMessage
from pyd2bot.misc.Localizer import BankInfos, Localizer

logger = Logger()
        
class SellerStateEnum:
    WATING_MAP = 0
    IDLE = 4
    GOING_TO_BANK = 1
    INSIDE_BANK = 8
    TREATING_BOT_UNLOAD = 2
    UNLOADING_IN_BANK = 3
    WAITING_FOR_BOT_TO_ARRIVE = 5
    EXCHANGING_WITH_GUEST = 6
    EXCHANGE_OPEN_REQUEST_RECEIVED = 7
    EXCHANGE_OPEN = 9
    EXCHANGE_ACCEPT_SENT = 10
    

class BotSellerCollectFrame(Frame):
    PHENIX_MAPID = None
    
    def __init__(self, bankInfos: BankInfos, guest: dict):
        self.guest = guest
        self.bankInfos = bankInfos
        super().__init__()

    def pushed(self) -> bool:
        logger.debug("BotUnloadInBankFrame pushed")
        self.state = SellerStateEnum.WATING_MAP
        if PlayedCharacterManager().currentMap is not None:
            self.state = SellerStateEnum.GOING_TO_BANK
            self.goToBank()
        return True

    def pulled(self) -> bool:
        logger.debug("BotUnloadInBankFrame pulled")
        return True

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    def goToBank(self):
        currentMapId = PlayedCharacterManager().currentMap.mapId
        if currentMapId != self.bankInfos.npcMapId:
            Kernel().getWorker().addFrame(BotAutoTripFrame(self.bankInfos.npcMapId))
        else:
            self.state = SellerStateEnum.WAITING_FOR_BOT_TO_ARRIVE
            

    def process(self, msg: Message) -> bool:
    
        if isinstance(msg, AutoTripEndedMessage):
            logger.debug("AutoTripEndedMessage received")
            if self.state == SellerStateEnum.GOING_TO_BANK:
                self.state = SellerStateEnum.INSIDE_BANK
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            if self.state == SellerStateEnum.WATING_MAP:
                logger.debug("MapComplementaryInformationsDataMessage received")
                self.state = SellerStateEnum.GOING_TO_BANK
                self.goToBank()
        
        elif isinstance(msg, ExchangeRequestedTradeMessage):
            if msg.source == self.guest["id"]:
                self.state = SellerStateEnum.EXCHANGE_OPEN_REQUEST_RECEIVED
                ConnectionsHandler.getConnection().send(ExchangeAcceptMessage())
                
        elif isinstance(msg, ExchangeStartedWithPodsMessage):
            self.state = SellerStateEnum.EXCHANGE_OPEN
            logger.debug("ExchangeStartedWithPodsMessage received")
            return True
        
        elif isinstance(msg, ExchangeIsReadyMessage):
            if msg.id == self.guest["id"]:
                logger.debug("ExchangeIsReadyMessage received")
                resp = ExchangeReadyMessage()
                resp.init(ready_=True, step_=1)
                ConnectionsHandler.getConnection().send(resp)
                self.state = SellerStateEnum.EXCHANGE_ACCEPT_SENT
                return True
        
        elif isinstance(msg, ExchangeLeaveMessage):
            logger.debug("ExchangeLeaveMessage received")
            self.state = SellerStateEnum.UNLOADING_IN_BANK
            Kernel().getWorker().addFrame(BotBankInteractionFrame(self.bankInfos))
        
        elif isinstance(msg, BankInteractionEndedMessage):
            logger.debug("BankInteractionEndedMessage received")
            self.state  = SellerStateEnum.IDLE
            Kernel().getWorker().removeFrame(self)

    def startExchangeWithGuest(self):
        msg = ExchangePlayerRequestMessage()
        msg.init(exchangeType_=1, target_=self.guest["id"])
        ConnectionsHandler.getConnection().send(msg)
        self.state = SellerStateEnum.EXCHANGE_OPEN_REQUEST_RECEIVED
        logger.debug("Exchange open request sent")
        
 