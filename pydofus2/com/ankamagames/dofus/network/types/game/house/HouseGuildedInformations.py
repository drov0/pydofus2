from pydofus2.com.ankamagames.dofus.network.types.game.house.HouseInstanceInformations import HouseInstanceInformations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.GuildInformations import GuildInformations
    from pydofus2.com.ankamagames.dofus.network.types.common.AccountTagInformation import AccountTagInformation


class HouseGuildedInformations(HouseInstanceInformations):
    guildInfo: "GuildInformations"

    def init(
        self,
        guildInfo_: "GuildInformations",
        instanceId_: int,
        ownerTag_: "AccountTagInformation",
        price_: int,
        secondHand_: bool,
        isLocked_: bool,
        hasOwner_: bool,
        isSaleLocked_: bool,
        isAdminLocked_: bool,
    ):
        self.guildInfo = guildInfo_

        super().init(instanceId_, ownerTag_, price_, secondHand_, isLocked_, hasOwner_, isSaleLocked_, isAdminLocked_)
