from dataclasses import dataclass
from com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from com.ankamagames.dofus.network.types.game.context.roleplay.party.DungeonPartyFinderPlayer import DungeonPartyFinderPlayer


@dataclass
class DungeonPartyFinderRoomContentMessage(NetworkMessage):
    dungeonId:int
    players:list[DungeonPartyFinderPlayer]
    
    
    def __post_init__(self):
        super().__init__()
    