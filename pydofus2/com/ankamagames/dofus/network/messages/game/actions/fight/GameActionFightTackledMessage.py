from pydofus2.com.ankamagames.dofus.network.messages.game.actions.AbstractGameActionMessage import AbstractGameActionMessage

class GameActionFightTackledMessage(AbstractGameActionMessage):
    tacklersIds: list[int]
    def init(self, tacklersIds_: list[int], actionId_: int, sourceId_: int):
        self.tacklersIds = tacklersIds_
        
        super().init(actionId_, sourceId_)
    