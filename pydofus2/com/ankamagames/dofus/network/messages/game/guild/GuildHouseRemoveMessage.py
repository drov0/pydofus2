from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage

class GuildHouseRemoveMessage(NetworkMessage):
    houseId: int
    instanceId: int
    secondHand: bool
    def init(self, houseId_: int, instanceId_: int, secondHand_: bool):
        self.houseId = houseId_
        self.instanceId = instanceId_
        self.secondHand = secondHand_
        
        super().__init__()
    