from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage

class AllianceRankCreateRequestMessage(NetworkMessage):
    parentRankId: int
    gfxId: int
    name: str
    def init(self, parentRankId_: int, gfxId_: int, name_: str):
        self.parentRankId = parentRankId_
        self.gfxId = gfxId_
        self.name = name_
        
        super().__init__()
    