from pydofus2.com.ankamagames.dofus.network.messages.game.context.GameMapMovementRequestMessage import GameMapMovementRequestMessage

class GameCautiousMapMovementRequestMessage(GameMapMovementRequestMessage):
    def init(self, keyMovements_: list[int], mapId_: int):
        
        super().init(keyMovements_, mapId_)
    