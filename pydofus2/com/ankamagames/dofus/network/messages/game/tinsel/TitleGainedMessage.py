from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage

class TitleGainedMessage(NetworkMessage):
    titleId: int
    def init(self, titleId_: int):
        self.titleId = titleId_
        
        super().__init__()
    