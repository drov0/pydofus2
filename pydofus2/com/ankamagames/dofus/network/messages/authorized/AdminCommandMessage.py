from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.Uuid import Uuid
    

class AdminCommandMessage(NetworkMessage):
    messageUuid: 'Uuid'
    content: str
    def init(self, messageUuid_: 'Uuid', content_: str):
        self.messageUuid = messageUuid_
        self.content = content_
        
        super().__init__()
    