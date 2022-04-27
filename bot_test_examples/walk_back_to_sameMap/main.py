from bot_test_examples.walk_back_to_sameMap.WalkMeToDestinationMapFrame import (
    WalkMeToDestinationMapFrame,
)
from pyd2bot.Bot import Bot
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)


if __name__ == "__main__":
    bot = Bot("grinder")
    bot._worker.addFrame(WalkMeToDestinationMapFrame(191104002))
    bot.start()
