from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.startup.GameActionItem import GameActionItem
    

class GameActionItemListMessage(NetworkMessage):
    actions: list['GameActionItem']
    def init(self, actions_: list['GameActionItem']):
        self.actions = actions_
        
        super().__init__()
    