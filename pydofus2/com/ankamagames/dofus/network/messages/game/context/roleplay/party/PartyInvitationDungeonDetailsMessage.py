from pydofus2.com.ankamagames.dofus.network.messages.game.context.roleplay.party.PartyInvitationDetailsMessage import (
    PartyInvitationDetailsMessage,
)
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.party.PartyInvitationMemberInformations import (
        PartyInvitationMemberInformations,
    )
    from pydofus2.com.ankamagames.dofus.network.types.game.context.roleplay.party.PartyGuestInformations import (
        PartyGuestInformations,
    )


class PartyInvitationDungeonDetailsMessage(PartyInvitationDetailsMessage):
    dungeonId: int
    playersDungeonReady: list[bool]

    def init(
        self,
        dungeonId_: int,
        playersDungeonReady_: list[bool],
        partyType_: int,
        partyName_: str,
        fromId_: int,
        fromName_: str,
        leaderId_: int,
        members_: list["PartyInvitationMemberInformations"],
        guests_: list["PartyGuestInformations"],
        partyId_: int,
    ):
        self.dungeonId = dungeonId_
        self.playersDungeonReady = playersDungeonReady_

        super().init(partyType_, partyName_, fromId_, fromName_, leaderId_, members_, guests_, partyId_)
