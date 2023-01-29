from pydofus2.com.ankamagames.jerakine.network.NetworkMessage import NetworkMessage
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.GuildInformations import GuildInformations


class GuildInvitedMessage(NetworkMessage):
    recruterId: int
    recruterName: str
    guildInfo: "GuildInformations"

    def init(self, recruterId_: int, recruterName_: str, guildInfo_: "GuildInformations"):
        self.recruterId = recruterId_
        self.recruterName = recruterName_
        self.guildInfo = guildInfo_

        super().__init__()
