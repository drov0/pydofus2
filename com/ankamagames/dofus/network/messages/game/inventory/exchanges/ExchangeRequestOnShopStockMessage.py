from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage


@dataclass
class ExchangeRequestOnShopStockMessage(NetworkMessage):
    
    
    def __post_init__(self):
        super().__init__()
    