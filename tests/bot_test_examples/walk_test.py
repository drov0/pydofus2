from com.ankamagames.atouin.managers.FrustumManager import FrustumManager
from com.ankamagames.dofus.network.messages.game.interactive.InteractiveUseRequestMessage import (
    InteractiveUseRequestMessage,
)
from pyd2bot.apis.FarmAPI import FarmAPI
from pyd2bot.main import Bot


bot = Bot("grinder")
bot.connect()
bot.mainConn.DEBUG_DATA = True
bot.waitInsideGameMap()
r = FrustumManager.getMapChangeDirections()
for e in r:
    print(e.name)
bot.stop()
