from bot_test_examples.farm_and_random_move.BotFarmFrame import BotFarmFrame
from pyd2bot.frames.BotGameApproach import BotGameApproach
from pyd2bot.Bot import Bot
from com.ankamagames.jerakine.logger.Logger import Logger
import threading

logger = Logger(__name__)

newMap = threading.Event()


if __name__ == "__main__":
    bot = Bot("grinder")
    bot._worker.addFrame(BotFarmFrame())
    bot.start()
