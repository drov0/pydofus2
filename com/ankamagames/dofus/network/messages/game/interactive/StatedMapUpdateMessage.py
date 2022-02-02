from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.interactive.StatedElement import StatedElement


@dataclass
class StatedMapUpdateMessage(NetworkMessage):
    statedElements:list[StatedElement]
    
    
    def __post_init__(self):
        super().__init__()
    