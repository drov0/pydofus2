from dataclasses import dataclass
from com.ankamagames.dofus.network.types.game.friend.FriendInformations import FriendInformations
from com.ankamagames.dofus.network.types.game.context.roleplay.GuildInformations import GuildInformations
from com.ankamagames.dofus.network.types.game.character.status.PlayerStatus import PlayerStatus


@dataclass
class FriendOnlineInformations(FriendInformations):
    playerId:int
    playerName:str
    level:int
    alignmentSide:int
    breed:int
    guildInfo:GuildInformations
    moodSmileyId:int
    status:PlayerStatus
    sex:bool
    havenBagShared:bool
    
    
    def __post_init__(self):
        super().__init__()
    