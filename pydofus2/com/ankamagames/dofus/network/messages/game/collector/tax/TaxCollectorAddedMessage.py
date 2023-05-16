from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.guild.tax.TaxCollectorInformations import TaxCollectorInformations
    

class TaxCollectorAddedMessage(NetworkMessage):
    callerId: int
    description: 'TaxCollectorInformations'
    def init(self, callerId_: int, description_: 'TaxCollectorInformations'):
        self.callerId = callerId_
        self.description = description_
        
        super().__init__()
    