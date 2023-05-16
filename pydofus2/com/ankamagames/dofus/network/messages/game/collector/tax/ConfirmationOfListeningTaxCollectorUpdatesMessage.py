from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.guild.tax.TaxCollectorInformations import TaxCollectorInformations
    

class ConfirmationOfListeningTaxCollectorUpdatesMessage(NetworkMessage):
    information: 'TaxCollectorInformations'
    def init(self, information_: 'TaxCollectorInformations'):
        self.information = information_
        
        super().__init__()
    