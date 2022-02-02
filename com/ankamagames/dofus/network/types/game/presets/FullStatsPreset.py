from dataclasses import dataclass
from com.ankamagames.dofus.network.types.game.presets.Preset import Preset
from com.ankamagames.dofus.network.types.game.presets.CharacterCharacteristicForPreset import CharacterCharacteristicForPreset


@dataclass
class FullStatsPreset(Preset):
    stats:list[CharacterCharacteristicForPreset]
    
    
    def __post_init__(self):
        super().__init__()
    