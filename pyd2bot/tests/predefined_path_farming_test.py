from com.DofusClient import DofusClient
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder
from pyd2bot.frames.BotFightFrame import BotFightFrame
from pyd2bot.frames.BotWorkflowFrame import BotWorkflowFrame
from pyd2bot.frames.BotFarmPathFrame import BotFarmPathFrame
from com.ankamagames.jerakine.logger.Logger import Logger
from pyd2bot.managers.BotCredsManager import BotCredsManager
from pyd2bot.models.farmPaths.RandomSubAreaFarmPath import RandomSubAreaFarmPath

logger = Logger("Dofus2")


if __name__ == "__main__":
    charachterId = "Moneydicer(210)"
    dofus2 = DofusClient()

    # setup the farm path
    ronce_spellId = 13516
    astrub_vilage_subareaId = 95
    astrub_forest_subareaId = 97
    incarnam_subareaId = 450
    astrub_tainela_subareaId = 30
    astrub_tainela_map = WorldPathFinder().worldGraph.getVertex(120062979.0, 1)
    astrub_bank_map = WorldPathFinder().worldGraph.getVertex(191104002.0, 1)
    astrub_forest_map = WorldPathFinder().worldGraph.getVertex(189532167.0, 1)
    incarnam_map = WorldPathFinder().worldGraph.getVertex(153880835.0, 1)
    lumberjackId = 2

    pioute_astrub_village = RandomSubAreaFarmPath(
        subAreaId=astrub_vilage_subareaId, startVertex=astrub_bank_map, fightOnly=True, monsterLvlCoefDiff=3
    )

    incarnam_monster = RandomSubAreaFarmPath(
        subAreaId=incarnam_subareaId, startVertex=incarnam_map, fightOnly=True, monsterLvlCoefDiff=3
    )

    tainela_bouftou = RandomSubAreaFarmPath(
        subAreaId=astrub_tainela_subareaId, startVertex=astrub_tainela_map, fightOnly=True, monsterLvlCoefDiff=1.5
    )

    lumberjack_astrub_forest = RandomSubAreaFarmPath(
        subAreaId=astrub_forest_subareaId, startVertex=astrub_forest_map, fightOnly=False, jobIds=[lumberjackId]
    )
    BotFightFrame.spellId = ronce_spellId
    BotFarmPathFrame.farmPath = tainela_bouftou

    dofus2.registerFrame(BotWorkflowFrame())
    creds = BotCredsManager.getEntry(charachterId)
    dofus2.login(**creds)
    dofus2.join()
