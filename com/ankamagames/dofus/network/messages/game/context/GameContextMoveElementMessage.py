from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.context.EntityMovementInformations import EntityMovementInformations


@dataclass
class GameContextMoveElementMessage(NetworkMessage):
    movement:EntityMovementInformations
    
    
    def __post_init__(self):
        super().__init__()
    