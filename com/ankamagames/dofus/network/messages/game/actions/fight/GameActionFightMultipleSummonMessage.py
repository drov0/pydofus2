from dataclasses import dataclass
from com.ankamagames.dofus.network.messages.game.actions.AbstractGameActionMessage import AbstractGameActionMessage
from com.ankamagames.dofus.network.types.game.context.fight.GameContextSummonsInformation import GameContextSummonsInformation


@dataclass
class GameActionFightMultipleSummonMessage(AbstractGameActionMessage):
    summons:list[GameContextSummonsInformation]
    
    
    def __post_init__(self):
        super().__init__()
    