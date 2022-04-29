from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.common.misc.Inventory import Inventory
import com.ankamagames.dofus.logic.game.common.managers.StorageOptionManager as storageoptmgr


class PlayerInventory(Inventory):
    def __init__(self):
        super().__init__()

    @property
    def kamas(self):
        raise RuntimeError("This property has no getter!")

    @kamas.setter
    def kamas(self, value: float) -> None:
        if PlayedCharacterManager().characteristics:
            PlayedCharacterManager().characteristics.kamas = value
        self._kamas = value
        storageoptmgr.StorageOptionManager().updateStorageView()
