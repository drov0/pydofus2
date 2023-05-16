from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.uuid import uuid
    

class MoveTaxCollectorPresetSpellMessage(NetworkMessage):
    presetId: 'uuid'
    movedFrom: int
    movedTo: int
    def init(self, presetId_: 'uuid', movedFrom_: int, movedTo_: int):
        self.presetId = presetId_
        self.movedFrom = movedFrom_
        self.movedTo = movedTo_
        
        super().__init__()
    