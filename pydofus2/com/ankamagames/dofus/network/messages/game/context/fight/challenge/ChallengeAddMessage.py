from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.fight.challenge.ChallengeInformation import ChallengeInformation
    

class ChallengeAddMessage(NetworkMessage):
    challengeInformation: 'ChallengeInformation'
    def init(self, challengeInformation_: 'ChallengeInformation'):
        self.challengeInformation = challengeInformation_
        
        super().__init__()
    