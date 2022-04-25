from com.ankamagames.atouin.managers.FrustumManager import FrustumManager
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseRequestMessage import (
    InteractiveUseRequestMessage,
)
from pyd2bot.apis.FarmAPI import FarmAPI
from pyd2bot.main import Bot


bot = Bot("shooter")
bot.connect()
bot.mainConn.DEBUG_DATA = True
bot.waitInsideGameMap()

FrustumManager.d

iurmsg = InteractiveUseRequestMessage()
iurmsg.init(515605, 140139437)
bot.mainConn.send(iurmsg)
