from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.prism.PrismGeolocalizedInformation import PrismGeolocalizedInformation
    

class PrismAddOrUpdateMessage(NetworkMessage):
    prism: 'PrismGeolocalizedInformation'
    def init(self, prism_: 'PrismGeolocalizedInformation'):
        self.prism = prism_
        
        super().__init__()
    