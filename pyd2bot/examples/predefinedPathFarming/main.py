from pyd2bot.examples.predefinedPathFarming.BotFarmPathFrame import BotFarmPathFrame
from pyd2bot.Bot import Bot
from com.ankamagames.jerakine.logger.Logger import Logger

from pyd2bot.examples.predefinedPathFarming.FarmParcours import FarmParcours

logger = Logger(__name__)

# Goujon path incarnam
FISHING_SKILL_ID = 124

goujon_incarnam = {
    "startMapId": 154010882,
    "path": [
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
    ],
    "skills": [FISHING_SKILL_ID],
}

if __name__ == "__main__":
    botName = "foobar"
    bot = Bot(botName)
    bot._worker.addFrame(
        BotFarmPathFrame(
            parcours=FarmParcours(**goujon_incarnam), skillsToUse=[FISHING_SKILL_ID]
        )
    )
    bot.start()
    bot.join()
