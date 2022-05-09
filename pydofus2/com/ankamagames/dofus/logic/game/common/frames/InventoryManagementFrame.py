from com.ankamagames.dofus.internalDatacenter.DataEnum import DataEnum
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.InventoryManager import (
    InventoryManager,
)
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import (
    PlayedCharacterManager,
)
from com.ankamagames.dofus.logic.game.roleplay.actions.DeleteObjectAction import (
    DeleteObjectAction,
)
from com.ankamagames.dofus.network.enums.CharacterInventoryPositionEnum import (
    CharacterInventoryPositionEnum,
)
from com.ankamagames.dofus.network.enums.ChatActivableChannelsEnum import (
    ChatActivableChannelsEnum,
)
from com.ankamagames.dofus.network.messages.game.inventory.KamasUpdateMessage import (
    KamasUpdateMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.InventoryContentMessage import (
    InventoryContentMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.InventoryWeightMessage import (
    InventoryWeightMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectAddedMessage import (
    ObjectAddedMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectDeleteMessage import (
    ObjectDeleteMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectDeletedMessage import (
    ObjectDeletedMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectDropMessage import (
    ObjectDropMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectModifiedMessage import (
    ObjectModifiedMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectMovementMessage import (
    ObjectMovementMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectQuantityMessage import (
    ObjectQuantityMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectUseOnCellMessage import (
    ObjectUseOnCellMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectUseOnCharacterMessage import (
    ObjectUseOnCharacterMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectsAddedMessage import (
    ObjectsAddedMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectsDeletedMessage import (
    ObjectsDeletedMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.ObjectsQuantityMessage import (
    ObjectsQuantityMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.WatchInventoryContentMessage import (
    WatchInventoryContentMessage,
)
from com.ankamagames.jerakine.benchmark.BenchmarkTimer import BenchmarkTimer
from com.ankamagames.jerakine.data.I18n import I18n
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.DataStoreType import DataStoreType
from com.ankamagames.jerakine.types.enums.Priority import Priority


class InventoryManagementFrame(Frame):

    logger = Logger("Dofus2")

    CHARACTER_BUILD_PRESET_TYPE: int = 1

    IDOLS_PRESET_TYPE: int = 2

    FORGETTABLE_PRESET_TYPE: int = 3

    POPUP_WARNING_TIPS_ID: int = 15

    _dataStoreType: DataStoreType

    popupSaveKeyClassic: str = "prevention-phishing"

    _objectUIDToDrop: int

    _objectGIDToDrop: int

    _quantityToDrop: int

    _dropPopup: str

    _currentPointUseUIDObject: int

    _movingObjectUID: int

    _movingObjectPreviousPosition: int

    _objectPositionModification: bool

    _presetTypeIdByPresetId: dict

    _waitTimer: BenchmarkTimer

    _chatText: str

    def __init__(self):
        super().__init__()

    @property
    def priority(self) -> int:
        return Priority.NORMAL

    def pushed(self) -> bool:
        InventoryManager().init()
        return True

    def process(self, msg: Message) -> bool:

        if isinstance(msg, WatchInventoryContentMessage):
            InventoryManager().init()
            wicmsg = msg
            InventoryManager().inventory.initializeFromObjectItems(wicmsg.objects)
            InventoryManager().inventory.kamas = wicmsg.kamas
            return True

        if isinstance(msg, InventoryContentMessage):
            icmsg = msg
            InventoryManager().inventory.initializeFromObjectItems(icmsg.objects)
            InventoryManager().inventory.kamas = icmsg.kamas
            equipmentView = InventoryManager().inventory.getView("equipment")
            if equipmentView and equipmentView.content:
                if (
                    equipmentView.content[CharacterInventoryPositionEnum.ACCESSORY_POSITION_PETS]
                    and equipmentView.content[CharacterInventoryPositionEnum.ACCESSORY_POSITION_PETS].typeId
                    == DataEnum.ITEM_TYPE_PETSMOUNT
                ):
                    PlayedCharacterManager().isPetsMounting = True
                    PlayedCharacterManager().petsMount = equipmentView.content[
                        CharacterInventoryPositionEnum.ACCESSORY_POSITION_PETS
                    ]
                if equipmentView.content[CharacterInventoryPositionEnum.INVENTORY_POSITION_ENTITY]:
                    PlayedCharacterManager().hasCompanion = True
            playerCharacterManager = PlayedCharacterManager()
            playerCharacterManager.inventory = InventoryManager().realInventory
            if playerCharacterManager.characteristics:
                playerCharacterManager.characteristics.kamas = icmsg.kamas
            return True

        if isinstance(msg, ObjectAddedMessage):
            oam = msg
            InventoryManager().inventory.addObjectItem(oam.object)
            return True

        if isinstance(msg, ObjectsAddedMessage):
            osam = msg
            for osait in osam.object:
                InventoryManager().inventory.addObjectItem(osait)
            return True

        if isinstance(msg, ObjectQuantityMessage):
            oqm = msg
            InventoryManager().inventory.modifyItemQuantity(oqm.objectUID, oqm.quantity)
            for shortcutQty in InventoryManager().shortcutBarItems:
                if shortcutQty and shortcutQty.id == oqm.objectUID:
                    shortcutQty.quantity = oqm.quantity
            return True

        if isinstance(msg, ObjectsQuantityMessage):
            osqm = msg
            for objoqm in osqm.objectsUIDAndQty:
                InventoryManager().inventory.modifyItemQuantity(objoqm.objectUID, objoqm.quantity)
                for shortcutsQty in InventoryManager().shortcutBarItems:
                    if shortcutsQty and shortcutsQty.id == objoqm.objectUID:
                        shortcutsQty.quantity = objoqm.quantity
            return True

        if isinstance(msg, KamasUpdateMessage):
            kumsg = msg
            InventoryManager().inventory.kamas = kumsg.kamasTotal
            InventoryManager().inventory.releaseHooks()
            return True

        if isinstance(msg, InventoryWeightMessage):
            iwmsg = msg
            PlayedCharacterManager().inventoryWeight = iwmsg.inventoryWeight
            PlayedCharacterManager().shopWeight = iwmsg.shopWeight
            PlayedCharacterManager().inventoryWeightMax = iwmsg.weightMax
            return False

        if isinstance(msg, ObjectMovementMessage):
            ommsg = msg
            InventoryManager().inventory.modifyItemPosition(ommsg.objectUID, ommsg.position)
            return True

        if isinstance(msg, ObjectModifiedMessage):
            omdmsg = msg
            inventoryMgr = InventoryManager()
            inventoryMgr.inventory.modifyObjectItem(omdmsg.object)
            return False

        if isinstance(msg, ObjectDeletedMessage):
            odmsg = msg
            InventoryManager().inventory.removeItem(odmsg.objectUID, -1)
            return True

        if isinstance(msg, ObjectsDeletedMessage):
            osdmsg = msg
            for osdit in osdmsg.objectUID:
                InventoryManager().inventory.removeItem(osdit, -1)
            return True

        if isinstance(msg, DeleteObjectAction):
            doa = msg
            odmsg2 = ObjectDeleteMessage()
            odmsg2.init(doa.objectUID, doa.quantity)
            ConnectionsHandler.getConnection().send(odmsg2)
            return True

        return False

    def pulled(self) -> bool:
        return True

    def onAcceptDrop(self) -> None:
        self._dropPopup = None
        odropmsg: ObjectDropMessage = ObjectDropMessage()
        odropmsg.initObjectDropMessage(self._objectUIDToDrop, self._quantityToDrop)
        if not PlayedCharacterManager().isFighting:
            ConnectionsHandler.getConnection().send(odropmsg)

    def onRefuseDrop(self) -> None:
        self._dropPopup = None
