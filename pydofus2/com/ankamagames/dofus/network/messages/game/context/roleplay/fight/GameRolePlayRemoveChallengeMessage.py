from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage

class GameRolePlayRemoveChallengeMessage(NetworkMessage):
    fightId: int
    def init(self, fightId_: int):
        self.fightId = fightId_
        
        super().__init__()
    