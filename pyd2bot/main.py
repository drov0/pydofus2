from com.DofusClient import DofusClient
from com.ankamagames.dofus.modules.utils.pathFinding.world.WorldPathFinder import WorldPathFinder
from pyd2bot.logic.frames.BotFightFrame import BotFightFrame
from pyd2bot.logic.frames.BotWorkflowFrame import BotWorkflowFrame
from pyd2bot.logic.frames.BotFarmPathFrame import BotFarmPathFrame
from com.ankamagames.jerakine.logger.Logger import Logger
from pyd2bot.logic.managers.BotCredsManager import BotCredsManager
from pyd2bot.logic.managers.PathManager import PathManager
from pyd2bot.logic.managers.SessionManager import SessionManager

logger = Logger("Dofus2")

if __name__ == "__main__":
    DofusClient.LOG_MEMORY_USAGE = True
    session = SessionManager.getSession("sadida-lumberjacker")
    dofus2 = DofusClient()
    BotFightFrame.spellId = session.spellId
    BotFarmPathFrame.farmPath = session.path
    dofus2.registerFrame(BotWorkflowFrame())
    dofus2.login(**session.creds)
    dofus2.join()
