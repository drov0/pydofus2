from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.mount.MountClientData import MountClientData


@dataclass
class MountSetMessage(NetworkMessage):
    mountData:MountClientData
    
    
    def __post_init__(self):
        super().__init__()
    