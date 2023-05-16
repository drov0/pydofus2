from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.AllianceInformation import AllianceInformation
    from pydofus2.com.ankamagames.dofus.network.types.game.alliance.KohAllianceRoleMembers import KohAllianceRoleMembers
    from pydofus2.com.ankamagames.dofus.network.types.game.alliance.KohScore import KohScore
    

class KohAllianceInfo(NetworkMessage):
    alliance: 'AllianceInformation'
    memberCount: int
    kohAllianceRoleMembers: list['KohAllianceRoleMembers']
    scores: list['KohScore']
    matchDominationScores: int
    def init(self, alliance_: 'AllianceInformation', memberCount_: int, kohAllianceRoleMembers_: list['KohAllianceRoleMembers'], scores_: list['KohScore'], matchDominationScores_: int):
        self.alliance = alliance_
        self.memberCount = memberCount_
        self.kohAllianceRoleMembers = kohAllianceRoleMembers_
        self.scores = scores_
        self.matchDominationScores = matchDominationScores_
        
        super().__init__()
    