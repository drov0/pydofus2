from pyd2bot.frames.BotFarmFrame import BotFarmFrame
from pyd2bot.DofusClient import DofusClient
from com.ankamagames.jerakine.logger.Logger import Logger

logger = Logger(__name__)

if __name__ == "__main__":
    botName = "grinder"
    bot = DofusClient(botName)
    bot.registerFrame(BotFarmFrame())
    bot.start()
    bot.join()
