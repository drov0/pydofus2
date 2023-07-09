from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.challenge.ChallengeInformation import ChallengeInformation
    

class ChallengeProposalMessage(NetworkMessage):
    challengeProposals: list['ChallengeInformation']
    timer: int
    def init(self, challengeProposals_: list['ChallengeInformation'], timer_: int):
        self.challengeProposals = challengeProposals_
        self.timer = timer_
        
        super().__init__()
    