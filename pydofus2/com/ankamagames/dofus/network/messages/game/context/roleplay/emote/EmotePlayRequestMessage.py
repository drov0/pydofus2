from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage


class EmotePlayRequestMessage(NetworkMessage):
    emoteId:int
    

    def init(self, emoteId_:int):
        self.emoteId = emoteId_
        
        super().__init__()
    