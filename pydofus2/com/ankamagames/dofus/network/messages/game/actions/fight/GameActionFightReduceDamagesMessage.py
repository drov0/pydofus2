from pydofus2.com.ankamagames.dofus.network.messages.game.actions.AbstractGameActionMessage import AbstractGameActionMessage

class GameActionFightReduceDamagesMessage(AbstractGameActionMessage):
    targetId: int
    amount: int
    def init(self, targetId_: int, amount_: int, actionId_: int, sourceId_: int):
        self.targetId = targetId_
        self.amount = amount_
        
        super().init(actionId_, sourceId_)
    