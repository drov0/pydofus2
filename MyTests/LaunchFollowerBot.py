from com.DofusClient import DofusClient
from com.ankamagames.jerakine.logger.Logger import Logger
from pyd2bot.logic.common.frames.BotCharachterUpdatesFrame import BotCharachterUpdatesFrame
from pyd2bot.logic.common.frames.BotWorkflowFrame import BotWorkflowFrame
from pyd2bot.logic.fight.frames.BotFightFrame import BotFightFrame
from pyd2bot.logic.roleplay.frames.BotPartyFrame import BotPartyFrame
from pyd2bot.logic.managers.SessionManager import SessionManager


logger = Logger("Dofus2")

if __name__ == "__main__":
    sessionId = "sadida-follower"
    SessionManager().load(sessionId)
    dofus2 = DofusClient()
    dofus2.registerFrame(BotWorkflowFrame())
    dofus2.login(**SessionManager().creds)
    dofus2.join()
# ronce multiple
# 13524
