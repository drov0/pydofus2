from pydofus2.com.ankamagames.dofus.network.types.game.guild.logbook.GuildLogbookEntryBasicInformation import GuildLogbookEntryBasicInformation
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.guild.GuildRankMinimalInformation import GuildRankMinimalInformation
    

class GuildPlayerRankUpdateActivity(GuildLogbookEntryBasicInformation):
    guildRankMinimalInfos: 'GuildRankMinimalInformation'
    sourcePlayerId: int
    targetPlayerId: int
    sourcePlayerName: str
    targetPlayerName: str
    def init(self, guildRankMinimalInfos_: 'GuildRankMinimalInformation', sourcePlayerId_: int, targetPlayerId_: int, sourcePlayerName_: str, targetPlayerName_: str, id_: int, date_: int):
        self.guildRankMinimalInfos = guildRankMinimalInfos_
        self.sourcePlayerId = sourcePlayerId_
        self.targetPlayerId = targetPlayerId_
        self.sourcePlayerName = sourcePlayerName_
        self.targetPlayerName = targetPlayerName_
        
        super().init(id_, date_)
    