from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeObjectMessage import ExchangeObjectMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.data.items.ObjectItem import ObjectItem
    

class ExchangeObjectModifiedInBagMessage(ExchangeObjectMessage):
    object: 'ObjectItem'
    def init(self, object_: 'ObjectItem', remote_: bool):
        self.object = object_
        
        super().init(remote_)
    