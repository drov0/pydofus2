from threading import Timer
from pydofus2.com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from pydofus2.com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from pydofus2.com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.MapInformationsRequestMessage import (
    MapInformationsRequestMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.npc.NpcDialogCreationMessage import (
    NpcDialogCreationMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.npc.NpcDialogReplyMessage import (
    NpcDialogReplyMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.npc.NpcGenericActionRequestMessage import (
    NpcGenericActionRequestMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.dialog.LeaveDialogRequestMessage import LeaveDialogRequestMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseErrorMessage import (
    InteractiveUseErrorMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.interactive.InteractiveUsedMessage import InteractiveUsedMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeLeaveMessage import ExchangeLeaveMessage
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeObjectTransfertAllFromInvMessage import (
    ExchangeObjectTransfertAllFromInvMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeStartedWithStorageMessage import (
    ExchangeStartedWithStorageMessage,
)
from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.items.InventoryWeightMessage import InventoryWeightMessage

from pydofus2.com.ankamagames.jerakine.messages.Frame import Frame
from pydofus2.com.ankamagames.dofus.kernel.Kernel import Kernel
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.ankamagames.jerakine.messages.Message import Message
from pydofus2.com.ankamagames.jerakine.types.enums.Priority import Priority
from pyd2bot.logic.roleplay.frames.BotAutoTripFrame import BotAutoTripFrame
from pyd2bot.logic.roleplay.messages.AutoTripEndedMessage import AutoTripEndedMessage
from pyd2bot.logic.roleplay.messages.BankUnloadEndedMessage import BankUnloadEndedMessage
from pyd2bot.logic.roleplay.messages.BankUnloadFailedMessage import BankUnloadFailedMessage
from pyd2bot.misc.Localizer import Localizer

logger = Logger("Dofus2")


class BotUnloadInBankFrame(Frame):
    PHENIX_MAPID = None

    def __init__(self):
        super().__init__()

    def pushed(self) -> bool:
        logger.debug("BotUnloadInBankFrame pushed")
        self._askedEnterBank = False
        self._waitmap = True
        self._requestedUnload = False
        if PlayedCharacterManager().currentMap is not None:
            self._waitmap = False
            self.start()
        return True

    def pulled(self) -> bool:
        logger.debug("BotUnloadInBankFrame pulled")
        return True

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    def start(self):
        self.infos = Localizer.getBankInfos()
        logger.debug("Bank infos: %s", self.infos.__dict__)
        currentMapId = PlayedCharacterManager().currentMap.mapId
        self._startMapId = currentMapId
        self._startRpZone = PlayedCharacterManager().currentZoneRp
        self._enterBankFails = 0
        self._startedInBankMap = False
        if currentMapId != self.infos.npcMapId:
            Kernel().getWorker().addFrame(BotAutoTripFrame(self.infos.npcMapId))
        else:
            self._startedInBankMap = True
            self.talkToBankMan()

    def process(self, msg: Message) -> bool:

        if isinstance(msg, AutoTripEndedMessage):
            logger.debug("AutoTripEndedMessage received")
            if not self._startedInBankMap and msg.mapId == self._startMapId:
                Kernel().getWorker().removeFrame(self)
                Kernel().getWorker().processImmediately(BankUnloadEndedMessage())
            else:
                self.talkToBankMan()
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            if self._waitmap:
                self._waitmap = False
                self.start()

        elif isinstance(msg, NpcDialogCreationMessage):
            logger.debug("bank man dialog engaged")
            rmsg = NpcDialogReplyMessage()
            rmsg.init(self.infos.openBankReplyId)
            ConnectionsHandler.getConnection().send(rmsg)
            logger.debug("Bank reply to open bank storage sent")
            return True

        elif isinstance(msg, ExchangeStartedWithStorageMessage):
            self._requestedUnload = True
            rmsg = ExchangeObjectTransfertAllFromInvMessage()
            rmsg.init()
            ConnectionsHandler.getConnection().send(rmsg)
            return True

        elif isinstance(msg, InventoryWeightMessage):
            if self._requestedUnload:
                self._requestedUnload = False
                rmsg = LeaveDialogRequestMessage()
                rmsg.init()
                ConnectionsHandler.getConnection().send(rmsg)
            return True

        elif isinstance(msg, ExchangeLeaveMessage):
            if not self._startedInBankMap:
                Kernel().getWorker().addFrame(BotAutoTripFrame(self._startMapId, self._startRpZone))
            else:
                Kernel().getWorker().removeFrame(self)
                Kernel().getWorker().processImmediately(BankUnloadEndedMessage())
            return True

        elif isinstance(msg, InteractiveUseErrorMessage):
            self._enterBankFails += 1
            if self._enterBankFails == 3:
                Kernel().getWorker().removeFrame(self)
                Kernel().getWorker().processImmediately(BankUnloadFailedMessage())
            else:
                mirmsg = MapInformationsRequestMessage()
                mirmsg.init(mapId_=MapDisplayManager().currentMapPoint.mapId)
                ConnectionsHandler.getConnection().send(mirmsg)
            return True

    def talkToBankMan(self):
        rmsg = NpcGenericActionRequestMessage()
        rmsg.init(self.infos.npcId, self.infos.npcActionId, self.infos.npcMapId)
        ConnectionsHandler.getConnection().send(rmsg)
        logger.debug("Open bank man dialog sent")
