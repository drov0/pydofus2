from pydofus2.com.ankamagames.dofus.network.types.game.presets.Preset import Preset
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.presets.SpellsPreset import SpellsPreset
    from pydofus2.com.ankamagames.dofus.network.types.game.presets.SpellForPreset import SpellForPreset
    

class ForgettableSpellsPreset(Preset):
    baseSpellsPreset: 'SpellsPreset'
    forgettableSpells: list['SpellForPreset']
    def init(self, baseSpellsPreset_: 'SpellsPreset', forgettableSpells_: list['SpellForPreset'], id_: int):
        self.baseSpellsPreset = baseSpellsPreset_
        self.forgettableSpells = forgettableSpells_
        
        super().init(id_)
    