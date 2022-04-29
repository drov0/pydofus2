from pyd2bot.examples.predefinedPathFarming.BotFarmPathFrame import BotFarmPathFrame
from pyd2bot.Bot import Bot
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)

# Goujon path incarnam
path = [
    (-2, -2),
    (-1, -2),
    (0, -2),
    (0, -1),
    (1, -1),
    (1, 0),
    (0, 0),
    (-1, 0),
    (-2, 0),
    (-2, -1),
    (-1, -1),
    (-1, -2),
]
FISHING_SKILL_ID = 124


if __name__ == "__main__":
    botName = "foobar"
    bot = Bot(botName)
    bot._worker.addFrame(BotFarmPathFrame(path=path, skillsToUse=[FISHING_SKILL_ID]))
    bot.start()
    bot.join()
