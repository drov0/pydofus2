from pydofus2.com.ankamagames.dofus.network.messages.game.actions.AbstractGameActionMessage import AbstractGameActionMessage

class GameActionFightPointsVariationMessage(AbstractGameActionMessage):
    targetId: int
    delta: int
    def init(self, targetId_: int, delta_: int, actionId_: int, sourceId_: int):
        self.targetId = targetId_
        self.delta = delta_
        
        super().init(actionId_, sourceId_)
    