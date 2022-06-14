from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage


class MapChangeFailedMessage(NetworkMessage):
    mapId: int

    def init(self, mapId):
        self.mapId = mapId
        super().__init__()
