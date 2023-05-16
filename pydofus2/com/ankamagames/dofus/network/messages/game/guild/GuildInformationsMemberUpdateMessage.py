from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.guild.GuildMemberInfo import GuildMemberInfo
    

class GuildInformationsMemberUpdateMessage(NetworkMessage):
    member: 'GuildMemberInfo'
    def init(self, member_: 'GuildMemberInfo'):
        self.member = member_
        
        super().__init__()
    