from pyd2bot.examples.farming.BotFarmFrame import BotFarmFrame
from pyd2bot.Bot import Bot
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)

if __name__ == "__main__":
    botName = "grinder"
    bot = Bot(botName)
    bot.registerFrame(BotFarmFrame())
    bot.start()
    bot.join()
