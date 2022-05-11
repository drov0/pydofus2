from time import sleep
from com.DofusClient import DofusClient
from com.ankamagames.dofus.logic.common.managers.PlayerManager import PlayerManager
from com.ankamagames.jerakine.logger.Logger import Logger
from launcher.AccountCredsManager import AccountCredsManager
from pyd2bot.managers.BotCredsManager import BotCredsManager

logger = Logger("Dofus2")

if __name__ == "__main__":
    accountId = "melanco"
    serverId = 210
    username = "maniac.depressif@gmail.com"
    password = "5hgCd.JMUVwxK-s"
    AccountCredsManager.addEntry(accountId, username, password)
    dofus2 = DofusClient()
    dofus2.login(accountId, serverId)
    while not PlayerManager().charactersList:
        sleep(0.2)
    for char in PlayerManager().charactersList:
        BotCredsManager.addEntry(f"{char.name}({serverId})", accountId, char.id, serverId)
    dofus2.shutdown()
