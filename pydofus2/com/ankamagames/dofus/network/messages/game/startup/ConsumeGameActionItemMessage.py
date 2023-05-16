from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage

class ConsumeGameActionItemMessage(NetworkMessage):
    actionId: int
    characterId: int
    def init(self, actionId_: int, characterId_: int):
        self.actionId = actionId_
        self.characterId = characterId_
        
        super().__init__()
    