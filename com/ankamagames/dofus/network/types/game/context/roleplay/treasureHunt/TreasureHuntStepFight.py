from dataclasses import dataclass
from com.ankamagames.dofus.network.types.game.context.roleplay.treasureHunt.TreasureHuntStep import TreasureHuntStep


@dataclass
class TreasureHuntStepFight(TreasureHuntStep):
    
    
    def __post_init__(self):
        super().__init__()
    