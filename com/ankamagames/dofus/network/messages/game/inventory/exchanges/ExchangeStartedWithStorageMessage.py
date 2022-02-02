from dataclasses import dataclass
from com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeStartedMessage import ExchangeStartedMessage


@dataclass
class ExchangeStartedWithStorageMessage(ExchangeStartedMessage):
    storageMaxSlot:int
    
    
    def __post_init__(self):
        super().__init__()
    