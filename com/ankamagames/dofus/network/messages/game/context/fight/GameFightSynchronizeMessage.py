from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.context.fight.GameFightFighterInformations import GameFightFighterInformations


@dataclass
class GameFightSynchronizeMessage(NetworkMessage):
    fighters:list[GameFightFighterInformations]
    
    
    def __post_init__(self):
        super().__init__()
    