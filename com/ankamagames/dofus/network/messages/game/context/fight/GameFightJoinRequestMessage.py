from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage


@dataclass
class GameFightJoinRequestMessage(NetworkMessage):
    fighterId:int
    fightId:int
    
    
    def __post_init__(self):
        super().__init__()
    