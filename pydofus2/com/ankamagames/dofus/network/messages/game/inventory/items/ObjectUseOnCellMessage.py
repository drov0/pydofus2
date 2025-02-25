from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.items.ObjectUseMessage import ObjectUseMessage

class ObjectUseOnCellMessage(ObjectUseMessage):
    cells: int
    def init(self, cells_: int, objectUID_: int):
        self.cells = cells_
        
        super().init(objectUID_)
    