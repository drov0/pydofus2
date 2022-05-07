from unittest import skip
from com.DofusClient import DofusClient
from pyd2bot.frames.BotContextFrame import BotContextFrame
from pyd2bot.frames.BotFarmPathFrame import BotFarmPathFrame
from com.ankamagames.jerakine.logger.Logger import Logger
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
pioute_astrub = {
    "startMapId": 191104002,
    "path": [(4, -18), (4, -19), (3, -19), (3, -18), (3, -17), (4, -17), (5, -17), (5, -18)],
    "skills": [],
    "fightOnly": True,
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
    BotFarmPathFrame.parcours = FarmParcours(**pioute_astrub)
    dofus2.registerFrame(BotContextFrame())
    dofus2.login(**creds)
    dofus2.join()
