from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.data.items.ObjectItemToSell import ObjectItemToSell


@dataclass
class ExchangeShopStockStartedMessage(NetworkMessage):
    objectsInfos:list[ObjectItemToSell]
    
    
    def __post_init__(self):
        super().__init__()
    