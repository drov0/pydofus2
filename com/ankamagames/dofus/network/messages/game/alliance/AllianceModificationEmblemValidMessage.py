from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.guild.GuildEmblem import GuildEmblem


@dataclass
class AllianceModificationEmblemValidMessage(NetworkMessage):
    Alliancemblem:GuildEmblem
    
    
    def __post_init__(self):
        super().__init__()
    