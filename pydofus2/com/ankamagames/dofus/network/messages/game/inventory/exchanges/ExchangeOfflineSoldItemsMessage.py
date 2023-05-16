from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.data.items.ObjectItemQuantityPriceDateEffects import ObjectItemQuantityPriceDateEffects
    

class ExchangeOfflineSoldItemsMessage(NetworkMessage):
    bidHouseItems: list['ObjectItemQuantityPriceDateEffects']
    def init(self, bidHouseItems_: list['ObjectItemQuantityPriceDateEffects']):
        self.bidHouseItems = bidHouseItems_
        
        super().__init__()
    