from dataclasses import dataclass
from com.ankamagames.dofus.network.types.game.data.items.Item import Item
from com.ankamagames.dofus.network.types.game.data.items.effects.ObjectEffect import ObjectEffect


@dataclass
class ObjectItem(Item):
    position:int
    objectGID:int
    effects:list[ObjectEffect]
    objectUID:int
    quantity:int
    
    
    def __post_init__(self):
        super().__init__()
    