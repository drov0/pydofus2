from dataclasses import dataclass
from com.ankamagames.dofus.network.messages.game.actions.AbstractGameActionMessage import AbstractGameActionMessage


@dataclass
class GameActionFightLifePointsLostMessage(AbstractGameActionMessage):
    targetId:int
    loss:int
    permanentDamages:int
    elementId:int
    
    
    def __post_init__(self):
        super().__init__()
    