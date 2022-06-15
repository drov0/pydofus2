import sys
from pyd2bot.logic.common.frames.BotWorkflowFrame import BotWorkflowFrame

from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pydofus2.com.DofusClient import DofusClient
from pyd2bot.logic.managers.SessionManager import SessionManager
from pydofus2.com.ankamagames.haapi.Haapi import Haapi


def runSession(sessionId):
    SessionManager().load(sessionId)
    Logger.charachter = SessionManager().charachterId
    dofus2 = DofusClient()
    dofus2.registerFrame(BotWorkflowFrame())
    dofus2.login(SessionManager().loginToken, SessionManager().charachter["serverId"], SessionManager().charachter["charachterId"])
    dofus2.join()


if __name__ == "__main__":
    sessionId = sys.argv[1]
    runSession(sessionId)
