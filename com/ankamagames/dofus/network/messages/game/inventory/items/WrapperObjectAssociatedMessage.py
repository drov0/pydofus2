from dataclasses import dataclass
from com.ankamagames.dofus.network.messages.game.inventory.items.SymbioticObjectAssociatedMessage import SymbioticObjectAssociatedMessage


@dataclass
class WrapperObjectAssociatedMessage(SymbioticObjectAssociatedMessage):
    
    
    def __post_init__(self):
        super().__init__()
    