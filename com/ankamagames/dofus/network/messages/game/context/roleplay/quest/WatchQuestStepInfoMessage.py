from dataclasses import dataclass
from com.ankamagames.dofus.network.messages.game.context.roleplay.quest.QuestStepInfoMessage import QuestStepInfoMessage


@dataclass
class WatchQuestStepInfoMessage(QuestStepInfoMessage):
    playerId:int
    
    
    def __post_init__(self):
        super().__init__()
    