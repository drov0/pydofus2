from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.BasicGuildInformations import BasicGuildInformations
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.guild.GuildEmblem import GuildEmblem
    


class GuildInformations(BasicGuildInformations):
    guildEmblem:'GuildEmblem'
    

    def init(self, guildEmblem_:'GuildEmblem', guildId_:int, guildName_:str, guildLevel_:int):
        self.guildEmblem = guildEmblem_
        
        super().init(guildId_, guildName_, guildLevel_)
    