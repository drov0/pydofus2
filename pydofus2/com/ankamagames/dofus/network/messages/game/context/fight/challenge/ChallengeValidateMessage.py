from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage

class ChallengeValidateMessage(NetworkMessage):
    challengeId: int
    def init(self, challengeId_: int):
        self.challengeId = challengeId_
        
        super().__init__()
    