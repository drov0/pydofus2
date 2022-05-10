from time import sleep
from unittest import skip
from com.DofusClient import DofusClient
from com.ankamagames.dofus.logic.game.common.managers.PlayedCharacterManager import PlayedCharacterManager
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldGraph import WorldGraph
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder
from pyd2bot.frames.BotWorkflowFrame import BotWorkflowFrame
from pyd2bot.frames.BotFarmPathFrame import BotFarmPathFrame
from com.ankamagames.jerakine.logger.Logger import Logger
from pyd2bot.managers.BotCredsManager import BotCredsManager
from pyd2bot.models.farmPaths.RandomSubAreaFarmPath import RandomSubAreaFarmPath

logger = Logger("Dofus2")

# Goujon path incarnam
FISHING_SKILL_ID = 124


if __name__ == "__main__":

    dofus2 = DofusClient()

    # setup the farm path
    astrub_vilage_subareaid = 95
    astrub_bank_map = WorldPathFinder().worldGraph.getVertex(191104002.0, 1)
    pioute_astrub = RandomSubAreaFarmPath(astrub_vilage_subareaid, astrub_bank_map, True, 1.5)

    BotFarmPathFrame.farmPath = pioute_astrub
    dofus2.registerFrame(BotWorkflowFrame())
    creds = BotCredsManager.getEntry("foobar")
    dofus2.login(**creds)
    dofus2.join()
