from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.uuid import uuid
    from pydofus2.com.ankamagames.dofus.network.types.game.collector.tax.TaxCollectorOrderedSpell import TaxCollectorOrderedSpell
    

class AddTaxCollectorPresetSpellMessage(NetworkMessage):
    presetId: 'uuid'
    spell: 'TaxCollectorOrderedSpell'
    def init(self, presetId_: 'uuid', spell_: 'TaxCollectorOrderedSpell'):
        self.presetId = presetId_
        self.spell = spell_
        
        super().__init__()
    