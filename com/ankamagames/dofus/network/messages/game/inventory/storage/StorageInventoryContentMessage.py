from dataclasses import dataclass
from com.ankamagames.dofus.network.messages.game.inventory.items.InventoryContentMessage import InventoryContentMessage


@dataclass
class StorageInventoryContentMessage(InventoryContentMessage):
    
    
    def __post_init__(self):
        super().__init__()
    