from dataclasses import dataclass
from com.ankamagames.dofus.network.types.game.context.fight.FightTeamInformations import FightTeamInformations


@dataclass
class FightAllianceTeamInformations(FightTeamInformations):
    relation:int
    
    
    def __post_init__(self):
        super().__init__()
    