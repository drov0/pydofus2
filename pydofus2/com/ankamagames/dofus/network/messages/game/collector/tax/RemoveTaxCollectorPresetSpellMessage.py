from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.uuid import uuid
    

class RemoveTaxCollectorPresetSpellMessage(NetworkMessage):
    presetId: 'uuid'
    slot: int
    def init(self, presetId_: 'uuid', slot_: int):
        self.presetId = presetId_
        self.slot = slot_
        
        super().__init__()
    