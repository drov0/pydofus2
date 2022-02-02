from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.data.items.ObjectItemGenericQuantity import ObjectItemGenericQuantity


@dataclass
class ExchangeBidHouseUnsoldItemsMessage(NetworkMessage):
    items:list[ObjectItemGenericQuantity]
    
    
    def __post_init__(self):
        super().__init__()
    