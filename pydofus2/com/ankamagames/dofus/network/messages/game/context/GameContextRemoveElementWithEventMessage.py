from pydofus2.com.ankamagames.dofus.network.messages.game.context.GameContextRemoveElementMessage import GameContextRemoveElementMessage

class GameContextRemoveElementWithEventMessage(GameContextRemoveElementMessage):
    elementEventId: int
    def init(self, elementEventId_: int, id_: int):
        self.elementEventId = elementEventId_
        
        super().init(id_)
    