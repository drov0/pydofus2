from com.ankamagames.jerakine.logger.Logger import Logger
from com.DofusClient import DofusClient
from pyd2bot.logic.common.frames.BotWorkflowFrame import BotWorkflowFrame
from pyd2bot.logic.managers.SessionManager import SessionManager
import sys


def runSession(sessionId):
    SessionManager().load(sessionId)
    Logger.charachter = SessionManager().charachterId
    dofus2 = DofusClient()
    dofus2.registerFrame(BotWorkflowFrame())
    dofus2.login(**SessionManager().creds)
    dofus2.join()


if __name__ == "__main__":
    sessionId = sys.argv[1]
    runSession(sessionId)
