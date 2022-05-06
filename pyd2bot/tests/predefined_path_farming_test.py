from com.DofusClient import DofusClient
from pyd2bot.frames.BotFarmPathFrame import BotFarmPathFrame
from com.ankamagames.jerakine.logger.Logger import Logger
from pyd2bot.frames.BotFightFrame import BotFightFrame
from pyd2bot.managers.BotCredsManager import BotCredsManager

from pyd2bot.models.FarmParcours import FarmParcours

logger = Logger("Dofus2")

# Goujon path incarnam
FISHING_SKILL_ID = 124

bouftou_incarnam = {
    "startMapId": 153879300,
    "path": [(1, -4), (0, -4), (0, -5), (1, -5)],
    "fightOnly": True,
    "skills": [FISHING_SKILL_ID],
}
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
    "fightOnly": True,
}

if __name__ == "__main__":
    botName = "foobar"
    creds = BotCredsManager.getEntry(botName)
    dofus2 = DofusClient()
    dofus2.registerFrame(BotFarmPathFrame(FarmParcours(**goujon_incarnam)))
    dofus2.registerFrame(BotFightFrame())
    dofus2.login(**creds)
    dofus2.join()
