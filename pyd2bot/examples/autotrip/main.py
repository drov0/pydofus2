from pyd2bot.examples.autotrip.WalkMeToDestinationMapFrame import (
    WalkMeToDestinationMapFrame,
)
from pyd2bot.Bot import Bot
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)


if __name__ == "__main__":
    botName = "grinder"
    bot = Bot(botName)
    bot.registerFrame(WalkMeToDestinationMapFrame(191104002))
    bot.start()
