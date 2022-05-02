from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.dofus.logic.game.common.managers.InventoryManager import (
    InventoryManager,
)
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.roleplay.actions.DeleteObjectAction import (
    DeleteObjectAction,
)


class InventoryAPI:
    @classmethod
    def getWeightPourcent(cls):
        pourcentt = (
            PlayedCharacterManager().inventoryWeight
            / PlayedCharacterManager().inventoryWeightMax
        ) * 100
        return pourcentt

    @classmethod
    def destroyAllItems(cls):
        for iw in InventoryManager().realInventory:
            doa = DeleteObjectAction.create(iw.objectUID, iw.quantity)
            Kernel().getWorker().process(doa)
