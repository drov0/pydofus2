from threading import Timer
from com.ankamagames.atouin.managers.MapDisplayManager import MapDisplayManager
from com.ankamagames.dofus.kernel.net.ConnectionsHandler import ConnectionsHandler
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapComplementaryInformationsDataMessage import (
    MapComplementaryInformationsDataMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.MapInformationsRequestMessage import (
    MapInformationsRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.npc.NpcDialogCreationMessage import (
    NpcDialogCreationMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.npc.NpcDialogReplyMessage import (
    NpcDialogReplyMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.npc.NpcGenericActionRequestMessage import (
    NpcGenericActionRequestMessage,
)
from com.ankamagames.dofus.network.messages.game.dialog.LeaveDialogRequestMessage import LeaveDialogRequestMessage
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseErrorMessage import (
    InteractiveUseErrorMessage,
)
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUsedMessage import InteractiveUsedMessage
from com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeLeaveMessage import ExchangeLeaveMessage
from com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeObjectTransfertAllFromInvMessage import (
    ExchangeObjectTransfertAllFromInvMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeStartedWithStorageMessage import (
    ExchangeStartedWithStorageMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.InventoryWeightMessage import InventoryWeightMessage

from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
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
        self._enterBankFails = 0
        if currentMapId != self.infos.npcMapId:
            Kernel().getWorker().addFrame(BotAutoTripFrame(self.infos.npcMapId))
        else:
            self.talkToBankMan()

    def process(self, msg: Message) -> bool:

        if isinstance(msg, AutoTripEndedMessage):
            logger.debug("AutoTripEndedMessage received")
            self.talkToBankMan()
            return True

        elif isinstance(msg, MapComplementaryInformationsDataMessage):
            if self._waitmap:
                self._waitmap = False
                self.start()

        elif isinstance(msg, NpcDialogCreationMessage):
            rmsg = NpcDialogReplyMessage()
            rmsg.init(self.infos.openBankReplyId)
            ConnectionsHandler.getConnection().send(rmsg)
            return True

        elif isinstance(msg, ExchangeStartedWithStorageMessage):
            rmsg = ExchangeObjectTransfertAllFromInvMessage()
            rmsg.init()
            ConnectionsHandler.getConnection().send(rmsg)
            return True

        elif isinstance(msg, InventoryWeightMessage):
            rmsg = LeaveDialogRequestMessage()
            rmsg.init()
            ConnectionsHandler.getConnection().send(rmsg)
            return True

        elif isinstance(msg, ExchangeLeaveMessage):
            Kernel().getWorker().removeFrame(self)
            Kernel().getWorker().process(BankUnloadEndedMessage())
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
