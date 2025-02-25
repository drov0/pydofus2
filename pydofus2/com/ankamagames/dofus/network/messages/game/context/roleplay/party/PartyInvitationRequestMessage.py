from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.common.AbstractPlayerSearchInformation import AbstractPlayerSearchInformation
    

class PartyInvitationRequestMessage(NetworkMessage):
    target: 'AbstractPlayerSearchInformation'
    def init(self, target_: 'AbstractPlayerSearchInformation'):
        self.target = target_
        
        super().__init__()
    