from com.DofusClient import DofusClient
from com.ankamagames.jerakine.logger.Logger import Logger
from pyd2bot.logic.common.frames.BotCharachterUpdatesFrame import BotCharachterUpdatesFrame
from pyd2bot.logic.fight.frames.BotFightFrame import BotFightFrame
from pyd2bot.logic.roleplay.frames.BotPartyFrame import BotPartyFrame
from pyd2bot.logic.managers.SessionManager import SessionManager


logger = Logger("Dofus2")

if __name__ == "__main__":
    sessionId = "sadida-lumberjacker"
    DofusClient.LOG_MEMORY_USAGE = False
    session = SessionManager.getSession(sessionId)
    dofus2 = DofusClient()
    BotCharachterUpdatesFrame.statIdToUp = session.statToUp
    BotPartyFrame.isLeader = False
    BotPartyFrame.leaderId = 336986964178
    BotPartyFrame.leaderName = "Plusbellelavie"
    BotFightFrame.spellId = session.spellId
    dofus2.registerFrame(BotPartyFrame())
    dofus2.registerFrame(BotFightFrame())
    dofus2.login(**session.creds)
    dofus2.join()
# ronce multiple
# 13524
