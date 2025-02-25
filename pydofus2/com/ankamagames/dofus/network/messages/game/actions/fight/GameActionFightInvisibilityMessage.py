from pydofus2.com.ankamagames.dofus.network.messages.game.actions.AbstractGameActionMessage import AbstractGameActionMessage

class GameActionFightInvisibilityMessage(AbstractGameActionMessage):
    targetId: int
    state: int
    def init(self, targetId_: int, state_: int, actionId_: int, sourceId_: int):
        self.targetId = targetId_
        self.state = state_
        
        super().init(actionId_, sourceId_)
    