from com.ankamagames.jerakine.logger.Logger import Logger
from com.DofusClient import DofusClient
from pyd2bot.logic.common.frames.BotCharachterUpdatesFrame import BotCharachterUpdatesFrame

from pyd2bot.logic.roleplay.frames.BotFarmPathFrame import BotFarmPathFrame
from pyd2bot.logic.fight.frames.BotFightFrame import BotFightFrame
from pyd2bot.logic.common.frames.BotWorkflowFrame import BotWorkflowFrame
from pyd2bot.logic.managers.SessionManager import SessionManager
import sys

logger = Logger("Dofus2")

if __name__ == "__main__":
<<<<<<< HEAD
    #SessionId = sys.argv[1]
    DofusClient.LOG_MEMORY_USAGE = False
    session = SessionManager.getSession("money_5")
=======
    sessionId = sys.argv[1]
    DofusClient.LOG_MEMORY_USAGE = False
    session = SessionManager.getSession(sessionId)
>>>>>>> 5ad21827988922e392c29e570dedd638679d6d00
    dofus2 = DofusClient()
    BotFightFrame.spellId = session.spellId
    BotFarmPathFrame.farmPath = session.path
    BotCharachterUpdatesFrame.statIdToUp = session.statToUp
    dofus2.registerFrame(BotWorkflowFrame())
    dofus2.login(**session.creds)
    dofus2.join()
