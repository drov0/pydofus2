from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.character.choice.CharacterBaseInformations import CharacterBaseInformations


@dataclass
class CharacterSelectedSuccessMessage(NetworkMessage):
    infos:CharacterBaseInformations
    isCollectingStats:bool
    
    
    def __post_init__(self):
        super().__init__()
    