from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.uuid import uuid
    from pydofus2.com.ankamagames.dofus.network.types.game.collector.tax.TaxCollectorOrderedSpell import TaxCollectorOrderedSpell
    

class TaxCollectorPresetSpellUpdatedMessage(NetworkMessage):
    presetId: 'uuid'
    taxCollectorSpells: list['TaxCollectorOrderedSpell']
    def init(self, presetId_: 'uuid', taxCollectorSpells_: list['TaxCollectorOrderedSpell']):
        self.presetId = presetId_
        self.taxCollectorSpells = taxCollectorSpells_
        
        super().__init__()
    