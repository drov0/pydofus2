from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.prism.PrismFightersInformation import PrismFightersInformation


@dataclass
class PrismFightAddedMessage(NetworkMessage):
    fight:PrismFightersInformation
    
    
    def __post_init__(self):
        super().__init__()
    