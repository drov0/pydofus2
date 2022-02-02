from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.character.alignment.ActorExtendedAlignmentInformations import ActorExtendedAlignmentInformations
from com.ankamagames.dofus.network.types.game.character.characteristic.CharacterCharacteristic import CharacterCharacteristic
from com.ankamagames.dofus.network.types.game.character.characteristic.CharacterSpellModification import CharacterSpellModification


@dataclass
class CharacterCharacteristicsInformations(NetworkMessage):
    experience:int
    experienceLevelFloor:int
    experienceNextLevelFloor:int
    experienceBonusLimit:int
    kamas:int
    alignmentInfos:ActorExtendedAlignmentInformations
    criticalHitWeapon:int
    characteristics:list[CharacterCharacteristic]
    spellModifications:list[CharacterSpellModification]
    probationTime:int
    
    
    def __post_init__(self):
        super().__init__()
    