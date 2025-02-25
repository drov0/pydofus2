from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage

class AllianceMemberOnlineStatusMessage(NetworkMessage):
    memberId: int
    online: bool
    def init(self, memberId_: int, online_: bool):
        self.memberId = memberId_
        self.online = online_
        
        super().__init__()
    