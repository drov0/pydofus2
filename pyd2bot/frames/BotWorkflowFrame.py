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
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from pyd2bot.frames.BotFightFrame import BotFightFrame
from pyd2bot.frames.BotFarmPathFrame import BotFarmPathFrame
from pyd2bot.frames.BotPhenixAutoRevive import BotPhenixAutoRevive

logger = Logger("Dofus2")


class BotWorkflowFrame(Frame):
    def __init__(self):
        self.currentContext = None
        super().__init__()

    def pushed(self) -> bool:
        return True

    def pulled(self) -> bool:
        return True

    @property
    def priority(self) -> int:
        return Priority.VERY_LOW

    def process(self, msg: Message) -> bool:

        if isinstance(msg, GameContextCreateMessage):
            self.currentContext = msg.context
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

        elif (
            isinstance(msg, GameRolePlayPlayerLifeStatusMessage)
            and (
                PlayerLifeStatusEnum(msg.state) == PlayerLifeStatusEnum.STATUS_TOMBSTONE
                or PlayerLifeStatusEnum(msg.state) == PlayerLifeStatusEnum.STATUS_PHANTOM
            )
        ) or isinstance(msg, GameRolePlayGameOverMessage):
            logger.debug(f"Player is dead, auto reviving...")
            if Kernel().getWorker().contains("BotFarmPathFrame"):
                Kernel().getWorker().removeFrameByName("BotFarmPathFrame")
            PlayedCharacterManager().state = PlayerLifeStatusEnum(msg.state)
            Kernel().getWorker().addFrame(BotPhenixAutoRevive(msg.phenixMapId))
            return False

        elif (
            isinstance(msg, GameRolePlayPlayerLifeStatusMessage)
            and PlayerLifeStatusEnum(msg.state) == PlayerLifeStatusEnum.STATUS_ALIVE_AND_KICKING
        ):
            logger.debug(f"Player is alive and kicking, returning to work...")
            if Kernel().getWorker().contains("BotPhenixAutoRevive"):
                Kernel().getWorker().removeFrameByName("BotPhenixAutoRevive")
            if not Kernel().getWorker().contains("BotFarmPathFrame"):
                Kernel().getWorker().addFrame(BotFarmPathFrame(True))
            return True
