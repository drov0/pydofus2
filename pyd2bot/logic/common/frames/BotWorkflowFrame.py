from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.network.enums.GameContextEnum import GameContextEnum
from com.ankamagames.dofus.network.enums.PlayerLifeStatusEnum import PlayerLifeStatusEnum
from com.ankamagames.dofus.network.messages.game.context.GameContextCreateMessage import GameContextCreateMessage
from com.ankamagames.dofus.network.messages.game.context.GameContextDestroyMessage import GameContextDestroyMessage
from com.ankamagames.dofus.network.messages.game.context.roleplay.death.GameRolePlayGameOverMessage import (
    GameRolePlayGameOverMessage,
)
from com.ankamagames.dofus.network.messages.game.context.roleplay.death.GameRolePlayPlayerLifeStatusMessage import (
    GameRolePlayPlayerLifeStatusMessage,
)
from com.ankamagames.dofus.network.messages.game.inventory.items.InventoryWeightMessage import InventoryWeightMessage
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from pyd2bot.apis.InventoryAPI import InventoryAPI
from pyd2bot.logic.common.frames.BotCharachterUpdatesFrame import BotCharachterUpdatesFrame
from pyd2bot.logic.fight.frames.BotFightFrame import BotFightFrame
from pyd2bot.logic.roleplay.frames.BotFarmPathFrame import BotFarmPathFrame
from pyd2bot.logic.roleplay.frames.BotPhenixAutoRevive import BotPhenixAutoRevive
from pyd2bot.logic.roleplay.frames.BotUnloadInBankFrame import BotUnloadInBankFrame
from pyd2bot.logic.roleplay.messages.BankUnloadEndedMessage import BankUnloadEndedMessage

logger = Logger("Dofus2")


class BotWorkflowFrame(Frame):
    def __init__(self):
        self.currentContext = None
        super().__init__()

    def pushed(self) -> bool:
        self._inBankAutoUnload = False
        self._inPhenixAutoRevive = False
        Kernel().getWorker().addFrame(BotCharachterUpdatesFrame())
        return True

    def pulled(self) -> bool:
        Kernel().getWorker().removeFrameByName("BotCharachterUpdatesFrame")
        return True

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    def process(self, msg: Message) -> bool:

        if isinstance(msg, GameContextCreateMessage):
            self.currentContext = msg.context
            if not self._inBankAutoUnload and not self._inPhenixAutoRevive:
                if self.currentContext == GameContextEnum.ROLE_PLAY:
                    Kernel().getWorker().addFrame(BotFarmPathFrame())

                elif self.currentContext == GameContextEnum.FIGHT:
                    Kernel().getWorker().addFrame(BotFightFrame())
            return True

        elif isinstance(msg, GameContextDestroyMessage):
            if self.currentContext == GameContextEnum.FIGHT:
                if Kernel().getWorker().getFrame("BotFightFrame"):
                    Kernel().getWorker().removeFrameByName("BotFightFrame")

            elif self.currentContext == GameContextEnum.ROLE_PLAY:
                if Kernel().getWorker().getFrame("BotFarmPathFrame"):
                    Kernel().getWorker().removeFrameByName("BotFarmPathFrame")
            return True

        elif isinstance(msg, InventoryWeightMessage):
            if not self._inBankAutoUnload:
                if InventoryAPI.getWeightPercent() > 95:
                    if Kernel().getWorker().getFrame("BotFarmPathFrame"):
                        Kernel().getWorker().removeFrameByName("BotFarmPathFrame")
                    self._inBankAutoUnload = True
                    logger.warn(
                        f"Inventory is almost full {InventoryAPI.getWeightPercent()}, will trigger auto bank unload..."
                    )
                    Kernel().getWorker().addFrame(BotUnloadInBankFrame())
                return True
            else:
                return False

        elif isinstance(msg, BankUnloadEndedMessage):
            self._inBankAutoUnload = False
            if not Kernel().getWorker().contains("BotFarmPathFrame"):
                Kernel().getWorker().addFrame(BotFarmPathFrame(True))
            if Kernel().getWorker().contains("BotUnloadInBankFrame"):
                Kernel().getWorker().removeFrameByName("BotUnloadInBankFrame")

        elif (
            isinstance(msg, GameRolePlayPlayerLifeStatusMessage)
            and (
                PlayerLifeStatusEnum(msg.state) == PlayerLifeStatusEnum.STATUS_TOMBSTONE
                or PlayerLifeStatusEnum(msg.state) == PlayerLifeStatusEnum.STATUS_PHANTOM
            )
        ) or isinstance(msg, GameRolePlayGameOverMessage):
            logger.debug(f"Player is dead, auto reviving...")
            self._inPhenixAutoRevive = True
            if Kernel().getWorker().contains("BotFarmPathFrame"):
                Kernel().getWorker().removeFrameByName("BotFarmPathFrame")
            PlayedCharacterManager().state = PlayerLifeStatusEnum(msg.state)
            Kernel().getWorker().addFrame(BotPhenixAutoRevive())
            return False

        elif (
            isinstance(msg, GameRolePlayPlayerLifeStatusMessage)
            and PlayerLifeStatusEnum(msg.state) == PlayerLifeStatusEnum.STATUS_ALIVE_AND_KICKING
        ):
            logger.debug(f"Player is alive and kicking, returning to work...")
            self._inPhenixAutoRevive = False
            if Kernel().getWorker().contains("BotPhenixAutoRevive"):
                Kernel().getWorker().removeFrameByName("BotPhenixAutoRevive")
            if not Kernel().getWorker().contains("BotFarmPathFrame"):
                Kernel().getWorker().addFrame(BotFarmPathFrame(True))
            return True
