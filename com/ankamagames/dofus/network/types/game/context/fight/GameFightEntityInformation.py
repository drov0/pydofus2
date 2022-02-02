from dataclasses import dataclass
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import GameFightFighterInformations


@dataclass
class GameFightEntityInformation(GameFightFighterInformations):
    entityModelId:int
    level:int
    masterId:int
    
    
    def __post_init__(self):
        super().__init__()
    