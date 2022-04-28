
from pyd2bot.examples.definedPathFarming.BotFarmPathFrame import BotFarmPathFrame
from pyd2bot.frames.BotGameApproach import BotGameApproach
from pyd2bot.Bot import Bot
from com.ankamagames.jerakine.logger.Logger import Logger
import threading
logger = Logger(__name__)

path = [[1,-32], 
        [1,-31],
        [2,-31],
        [2,-32]
        ]

            
        
if __name__ == "__main__":
    botName  = "botMeriana"
    bot = Bot(botName)
    bot._worker.addFrame(BotFarmPathFrame(path))
    bot.start()
    #getNextCoords(a)
