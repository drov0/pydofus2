from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage


class MapChangeFailedMessage(NetworkMessage):
    mapId: int
    reason: str

    def init(self, mapId, reason=""):
        self.mapId = mapId
        self.reason = reason
        super().__init__()
