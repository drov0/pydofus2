from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.data.items.ObjectItemQuantity import ObjectItemQuantity


@dataclass
class ObjectFeedMessage(NetworkMessage):
    objectUID:int
    meal:list[ObjectItemQuantity]
    
    
    def __post_init__(self):
        super().__init__()
    