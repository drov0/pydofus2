from pydofus2.com.ankamagames.dofus.network.messages.game.prism.PrismsListMessage import PrismsListMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.prism.PrismGeolocalizedInformation import PrismGeolocalizedInformation
    

class PrismsListUpdateMessage(PrismsListMessage):
    def init(self, prisms_: list['PrismGeolocalizedInformation']):
        
        super().init(prisms_)
    