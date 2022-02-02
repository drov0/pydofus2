from dataclasses import dataclass
from com.ankamagames.dofus.network.types.game.context.fight.FightTeamMemberInformations import FightTeamMemberInformations


@dataclass
class FightTeamMemberCharacterInformations(FightTeamMemberInformations):
    name:str
    level:int
    
    
    def __post_init__(self):
        super().__init__()
    