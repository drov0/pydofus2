from pydofus2.com.ankamagames.dofus.network.messages.game.prism.PrismsListMessage import PrismsListMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.prism.PrismSubareaEmptyInfo import PrismSubareaEmptyInfo
    


class PrismsListUpdateMessage(PrismsListMessage):
    

    def init(self, prisms_:list['PrismSubareaEmptyInfo']):
        
        super().init(prisms_)
    