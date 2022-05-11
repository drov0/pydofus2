import sys
from time import sleep
from com.DofusClient import DofusClient
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder
from pyd2bot.frames.BotFightFrame import BotFightFrame
from pyd2bot.frames.BotWorkflowFrame import BotWorkflowFrame
from pyd2bot.frames.BotFarmPathFrame import BotFarmPathFrame
from com.ankamagames.jerakine.logger.Logger import Logger
from pyd2bot.managers.BotCredsManager import BotCredsManager
from pyd2bot.managers.PathManager import PathManager

logger = Logger("Dofus2")

from collections import Counter
import linecache
import os
import tracemalloc


if __name__ == "__main__":

    # setup the farm path
    ronce_spellId = 13516
    truanderie_spellId = 12902
    charachterId = "Maniaco-lalcolic(210)"
    dofus2 = DofusClient()
    BotFightFrame.spellId = truanderie_spellId
    BotFarmPathFrame.farmPath = PathManager.getPath("lumberjack_astrub_forest")
    dofus2.registerFrame(BotWorkflowFrame())
    creds = BotCredsManager.getEntry(charachterId)
    counts = Counter()
    dofus2.LOG_MEMORY_USAGE = True
    dofus2.login(**creds)
    dofus2.join()
