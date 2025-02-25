from pydofus2.com.ankamagames.dofus.network.messages.game.actions.AbstractGameActionMessage import AbstractGameActionMessage

class GameActionFightCarryCharacterMessage(AbstractGameActionMessage):
    targetId: int
    cellId: int
    def init(self, targetId_: int, cellId_: int, actionId_: int, sourceId_: int):
        self.targetId = targetId_
        self.cellId = cellId_
        
        super().init(actionId_, sourceId_)
    