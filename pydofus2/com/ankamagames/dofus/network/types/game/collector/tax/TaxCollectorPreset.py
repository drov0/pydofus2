from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.uuid import uuid
    from pydofus2.com.ankamagames.dofus.network.types.game.collector.tax.TaxCollectorOrderedSpell import TaxCollectorOrderedSpell
    from pydofus2.com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristics import CharacterCharacteristics
    

class TaxCollectorPreset(NetworkMessage):
    presetId: 'uuid'
    spells: list['TaxCollectorOrderedSpell']
    characteristics: 'CharacterCharacteristics'
    def init(self, presetId_: 'uuid', spells_: list['TaxCollectorOrderedSpell'], characteristics_: 'CharacterCharacteristics'):
        self.presetId = presetId_
        self.spells = spells_
        self.characteristics = characteristics_
        
        super().__init__()
    