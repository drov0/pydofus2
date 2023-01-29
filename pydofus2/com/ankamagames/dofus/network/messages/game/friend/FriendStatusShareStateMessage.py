from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage


class FriendStatusShareStateMessage(NetworkMessage):
    share: bool

    def init(self, share_: bool):
        self.share = share_

        super().__init__()
