from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage

class NumericWhoIsRequestMessage(NetworkMessage):
    playerId: int
    def init(self, playerId_: int):
        self.playerId = playerId_
        
        super().__init__()
    