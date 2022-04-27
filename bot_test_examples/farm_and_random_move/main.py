from bot_test_examples.farm_and_random_move.BotFarmFrame import BotFarmFrame
from pyd2bot.Bot import Bot
from com.ankamagames.jerakine.logger.Logger import Logger
logger = Logger(__name__)

if __name__ == "__main__":
    botName  = "grinder"
    bot = Bot(botName)
    bot._worker.addFrame(BotFarmFrame())
    bot.start()
