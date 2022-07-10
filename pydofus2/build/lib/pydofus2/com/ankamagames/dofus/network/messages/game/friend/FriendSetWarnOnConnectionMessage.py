from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage


class FriendSetWarnOnConnectionMessage(NetworkMessage):
    enable:bool
    

    def init(self, enable_:bool):
        self.enable = enable_
        
        super().__init__()
    