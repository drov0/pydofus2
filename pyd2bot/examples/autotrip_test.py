from pyd2bot.frames.BotAutoTripFrame import (
    BotAutoTripFrame,
)
from pyd2bot.DofusClient import DofusClient
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)


if __name__ == "__main__":
    botName = "grinder"
    bot = DofusClient(botName)
    bot.registerFrame(BotAutoTripFrame(154010372))
    bot.start()
