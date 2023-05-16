from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.prism.PrismGeolocalizedInformation import PrismGeolocalizedInformation
    

class PrismsListMessage(NetworkMessage):
    prisms: list['PrismGeolocalizedInformation']
    def init(self, prisms_: list['PrismGeolocalizedInformation']):
        self.prisms = prisms_
        
        super().__init__()
    