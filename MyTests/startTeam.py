from multiprocessing import Process
from pydofus2.com.DofusClient import DofusClient
from pydofus2.com.ankamagames.jerakine.logger.Logger import Logger
from pyd2bot.logic.common.frames.BotWorkflowFrame import BotWorkflowFrame
from pyd2bot.logic.managers.SessionManager import SessionManager


def runSession(sessionId):
    SessionManager().load(sessionId)
    dofus2 = DofusClient()
    dofus2.registerInitFrame(BotWorkflowFrame())
    dofus2.login(**SessionManager().creds)
    dofus2.join()


if __name__ == "__main__":
    sessions = ["sadida-follower1", "sadida-follower2", "sadida-follower3", "sadida-leader"]
    processes = []
    for sessionId in sessions:
        p = Process(target=runSession, args=(sessionId,))
        p.start()
        processes.append(p)
