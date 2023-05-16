from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.rank.RankInformation import RankInformation
    

class UpdateGuildRankRequestMessage(NetworkMessage):
    rank: 'RankInformation'
    def init(self, rank_: 'RankInformation'):
        self.rank = rank_
        
        super().__init__()
    