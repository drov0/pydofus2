from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.interactive.InteractiveElement import InteractiveElement


@dataclass
class InteractiveMapUpdateMessage(NetworkMessage):
    interactiveElements:list[InteractiveElement]
    
    
    def __post_init__(self):
        super().__init__()
    