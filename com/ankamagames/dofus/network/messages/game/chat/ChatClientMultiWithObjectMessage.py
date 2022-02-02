from dataclasses import dataclass
from com.ankamagames.dofus.network.messages.game.chat.ChatClientMultiMessage import ChatClientMultiMessage
from com.ankamagames.dofus.network.types.game.data.items.ObjectItem import ObjectItem


@dataclass
class ChatClientMultiWithObjectMessage(ChatClientMultiMessage):
    objects:list[ObjectItem]
    
    
    def __post_init__(self):
        super().__init__()
    