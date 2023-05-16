from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.alliance.KothWinner import KothWinner
    

class KothEndMessage(NetworkMessage):
    winner: 'KothWinner'
    def init(self, winner_: 'KothWinner'):
        self.winner = winner_
        
        super().__init__()
    