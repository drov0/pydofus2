import pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayEntitiesFrame as ref
import pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayInteractivesFrame as rif
import pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayWorldFrame as rplWF
from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import \
    MapDisplayManager
from pydofus2.com.ankamagames.atouin.messages.MapLoadedMessage import \
    MapLoadedMessage
from pydofus2.com.ankamagames.berilia.managers.KernelEvent import KernelEvent
from pydofus2.com.ankamagames.berilia.managers.KernelEventsManager import \
    KernelEventsManager
from pydofus2.com.ankamagames.dofus.datacenter.world.SubArea import SubArea
from pydofus2.com.ankamagames.dofus.internalDatacenter.items.ItemWrapper import \
    ItemWrapper
from pydofus2.com.ankamagames.dofus.internalDatacenter.world.WorldPointWrapper import \
    WorldPointWrapper
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import \
    ConnectionsHandler
from pydofus2.com.ankamagames.dofus.logic.game.common.frames.CommonExchangeManagementFrame import \
    CommonExchangeManagementFrame
from pydofus2.com.ankamagames.dofus.logic.game.common.frames.ExchangeManagementFrame import \
    ExchangeManagementFrame
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import \
    PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.RoleplayMovementFrame import \
    RoleplayMovementFrame
from pydofus2.com.ankamagames.dofus.logic.game.roleplay.frames.ZaapFrame import \
    ZaapFrame
from pydofus2.com.ankamagames.dofus.network.enums.ExchangeTypeEnum import \
    ExchangeTypeEnum
from pydofus2.com.ankamagames.dofus.network.messages.game.context.GameContextDestroyMessage import \
    GameContextDestroyMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.CurrentMapInstanceMessage import \
    CurrentMapInstanceMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.CurrentMapMessage import \
    CurrentMapMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.havenbag.EnterHavenBagRequestMessage import \
    EnterHavenBagRequestMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.dialog.LeaveDialogMessage import \
    LeaveDialogMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.zaap.TeleportDestinationsMessage import \
    TeleportDestinationsMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.zaap.ZaapDestinationsMessage import \
    ZaapDestinationsMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeRequestedTradeMessage import \
    ExchangeRequestedTradeMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeStartedMessage import \
    ExchangeStartedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.items.ObtainedItemMessage import \
    ObtainedItemMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.items.ObtainedItemWithBonusMessage import \
    ObtainedItemWithBonusMessage
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority


class RoleplayContextFrame(Frame):
    def __init__(self):
        self._newCurrentMapIsReceived = False
        self._previousMapId = None
        self._priority = Priority.NORMAL
        self._listMapNpcsMsg = []
        super().__init__()

    @property
    def priority(self) -> int:
        return self._priority

    @priority.setter
    def priority(self, p: int) -> None:
        self._priority = p

    @property
    def previousMapId(self) -> float:
        return self._previousMapId

    @property
    def newCurrentMapIsReceived(self) -> bool:
        return self._newCurrentMapIsReceived

    @newCurrentMapIsReceived.setter
    def newCurrentMapIsReceived(self, value: bool) -> None:
        self._newCurrentMapIsReceived = value

    @property
    def entitiesFrame(self) -> ref.RoleplayEntitiesFrame:
        return self._entitiesFrame

    def pushed(self) -> bool:
        self.movementFrame = RoleplayMovementFrame()
        # self._worldFrame = rplWF.RoleplayWorldFrame()
        self._entitiesFrame = ref.RoleplayEntitiesFrame()
        self._interactivesFrame = rif.RoleplayInteractivesFrame()
        self._exchangeManagementFrame = ExchangeManagementFrame()
        self._zaapFrame = ZaapFrame()
        return True

    def havenbagEnter(self, ownerId=None):
        if ownerId is None:
            ownerId = PlayedCharacterManager().id
        enterhbrmsg = EnterHavenBagRequestMessage();
        enterhbrmsg.init(int(ownerId))
        ConnectionsHandler().send(enterhbrmsg)

    def process(self, msg: Message) -> bool:

        if isinstance(msg, CurrentMapMessage):
            KernelEventsManager().send(KernelEvent.CurrentMap, msg.mapId)
            Logger().debug(f"Loading roleplay map {msg.mapId}")
            self._newCurrentMapIsReceived = True
            newSubArea = SubArea.getSubAreaByMapId(msg.mapId)
            PlayedCharacterManager().currentSubArea = newSubArea
            if isinstance(msg, CurrentMapInstanceMessage):
                MapDisplayManager().mapInstanceId = msg.instantiatedMapId
            else:
                MapDisplayManager().mapInstanceId = 0
            wp = None
            Kernel().worker.pause()
            if self._entitiesFrame:
                Kernel().worker.removeFrame(self._entitiesFrame)
            # if self._worldFrame:
            #     Kernel().worker.removeFrame(self._worldFrame)
            if self._interactivesFrame:
                Kernel().worker.removeFrame(self._interactivesFrame)
            if self.movementFrame:
                Kernel().worker.removeFrame(self.movementFrame)
            if PlayedCharacterManager().isInHouse:
                wp = WorldPointWrapper(
                    msg.mapId,
                    True,
                    PlayedCharacterManager().currentMap.outdoorX,
                    PlayedCharacterManager().currentMap.outdoorY,
                )
            else:
                wp = WorldPointWrapper(int(msg.mapId))
            if PlayedCharacterManager().currentMap:
                self._previousMapId = PlayedCharacterManager().currentMap.mapId
            PlayedCharacterManager().currentMap = wp
            MapDisplayManager().loadMap(int(msg.mapId))
            return True

        elif isinstance(msg, MapLoadedMessage):
            Kernel().worker.addFrame(self._entitiesFrame)
            # Kernel().worker.addFrame(self._worldFrame)
            Kernel().worker.addFrame(self.movementFrame)
            Kernel().worker.addFrame(self._interactivesFrame)
            Kernel().worker.resume()
            KernelEventsManager().send(KernelEvent.MapLoaded, msg.id)
            self._listMapNpcsMsg = None
            return True

        elif isinstance(msg, GameContextDestroyMessage):
            Kernel().worker.removeFrame(self)
            return False

        elif isinstance(msg, ObtainedItemMessage):
            bonusQty = msg.bonusQuantity if isinstance(msg, ObtainedItemWithBonusMessage) else 0
            qty = msg.baseQuantity + bonusQty
            iw = ItemWrapper.create(0, 0, msg.genericId, 1, None)
            Logger().debug(f"Obtained item {iw.name} ({msg.genericId}) x {qty}")
            KernelEventsManager().send(KernelEvent.ObtainedItem, iw, qty)
            return True
        
        elif isinstance(msg, ExchangeRequestedTradeMessage):
            self.addCommonExchangeFrame(ExchangeTypeEnum.PLAYER_TRADE)
            if not Kernel().exchangeManagementFrame:
                Kernel().worker.addFrame(self._exchangeManagementFrame)
                Kernel().exchangeManagementFrame.processExchangeRequestedTradeMessage(msg)
            return True
        
        elif isinstance(msg, ExchangeStartedMessage):
            commonExchangeFrame = Kernel().commonExchangeManagementFrame
            if commonExchangeFrame:
                commonExchangeFrame.resetEchangeSequence()
            if msg.exchangeType in [ExchangeTypeEnum.CRAFT, ExchangeTypeEnum.MULTICRAFT_CRAFTER, ExchangeTypeEnum.MULTICRAFT_CUSTOMER, ExchangeTypeEnum.RUNES_TRADE]:
                self.addCraftFrame()
            elif msg.exchangeType in [ExchangeTypeEnum.BIDHOUSE_BUY, ExchangeTypeEnum.BIDHOUSE_SELL, ExchangeTypeEnum.PLAYER_TRADE, ExchangeTypeEnum.RECYCLE_TRADE]:
                pass  # Placeholder for the remaining cases
            self.addCommonExchangeFrame(msg.exchangeType)
            if not Kernel().worker.contains("ExchangeManagementFrame"):
                Kernel().worker.addFrame(self._exchangeManagementFrame)
            self._exchangeManagementFrame.process(msg)
            return True
        
        elif isinstance(msg, (ZaapDestinationsMessage, TeleportDestinationsMessage)):
            if not Kernel().worker.contains("ZaapFrame"):
                Kernel().worker.addFrame(self._zaapFrame);
                return self._zaapFrame.process(msg);
            return False;

        elif isinstance(msg, LeaveDialogMessage):
            KernelEventsManager().send(KernelEvent.DialogLeft)
            return False
        
        return False
    
    def addCommonExchangeFrame(self, exchangeType):
        if not Kernel().commonExchangeManagementFrame:
            self._commonExchangeFrame = CommonExchangeManagementFrame(exchangeType)
            Kernel().worker.addFrame(self._commonExchangeFrame)

    def pulled(self) -> bool:
        self._interactivesFrame.clear()
        Kernel().worker.removeFrame(self._entitiesFrame)
        # Kernel().worker.removeFrame(self._worldFrame)
        Kernel().worker.removeFrame(self.movementFrame)
        Kernel().worker.removeFrame(self._interactivesFrame)
        return True
