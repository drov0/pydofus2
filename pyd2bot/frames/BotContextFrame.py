from com.ankamagames.dofus.network.enums.GameContextEnum import GameContextEnum
from com.ankamagames.dofus.network.messages.game.context.GameContextCreateMessage import GameContextCreateMessage
from com.ankamagames.dofus.network.messages.game.context.GameContextDestroyMessage import GameContextDestroyMessage
from com.ankamagames.jerakine.messages.Frame import Frame
from com.ankamagames.dofus.kernel.Kernel import Kernel
from com.ankamagames.jerakine.logger.Logger import Logger
from com.ankamagames.jerakine.messages.Message import Message
from com.ankamagames.jerakine.types.enums.Priority import Priority
from pyd2bot.frames.BotFightFrame import BotFightFrame
from pyd2bot.frames.BotFarmPathFrame import BotFarmPathFrame

logger = Logger("Dofus2")


class BotContextFrame(Frame):
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
                    Kernel().getWorker().removeFrame(Kernel().getWorker().getFrame("BotFightFrame"))

            elif self.currentContext == GameContextEnum.ROLE_PLAY:
                if Kernel().getWorker().getFrame("BotFarmPathFrame"):
                    Kernel().getWorker().removeFrame(Kernel().getWorker().getFrame("BotFarmPathFrame"))
            return True
