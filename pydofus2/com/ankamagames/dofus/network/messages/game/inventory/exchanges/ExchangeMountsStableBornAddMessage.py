from pydofus2.com.ankamagames.dofus.network.messages.game.inventory.exchanges.ExchangeMountsStableAddMessage import ExchangeMountsStableAddMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.mount.MountClientData import MountClientData
    

class ExchangeMountsStableBornAddMessage(ExchangeMountsStableAddMessage):
    def init(self, mountDescription_: list['MountClientData']):
        
        super().init(mountDescription_)
    