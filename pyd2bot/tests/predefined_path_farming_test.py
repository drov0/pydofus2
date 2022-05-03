from pyd2bot.DofusClient import DofusClient
from pyd2bot.frames.BotFarmPathFrame import BotFarmPathFrame
from com.ankamagames.jerakine.logger.Logger import Logger
from pyd2bot.frames.BotFightFrame import BotFightFrame

from pyd2bot.models.FarmParcours import FarmParcours

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
    dofus2 = DofusClient(botName)
    dofus2.registerFrame(BotFarmPathFrame(FarmParcours(**goujon_incarnam)))
    dofus2.registerFrame(BotFightFrame())
    try:
        dofus2.start()
    except Exception as e:
        logger.error(e, exc_info=True)
    dofus2.join()
